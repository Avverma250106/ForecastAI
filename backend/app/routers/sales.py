from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import date
import pandas as pd
import io
import chardet
from app.models.inventory import Inventory
from app.database import get_db
from app.models.sale import Sale
from app.models.product import Product
from app.models.user import User
from app.schemas.sale import SaleCreate, SaleResponse, SalesUploadResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/sales", tags=["Sales"])


# ===================== GET SALES =====================
@router.get("/", response_model=List[SaleResponse])
def get_sales(
    skip: int = 0,
    limit: int = 1000,
    product_id: int = None,
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Sale).filter(Sale.user_id == current_user.id)

    if product_id:
        query = query.filter(Sale.product_id == product_id)
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)

    return query.order_by(Sale.sale_date.desc()).offset(skip).limit(limit).all()


# ===================== CREATE SALE =====================
@router.post("/", response_model=SaleResponse)
def create_sale(
    sale_data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(
        Product.id == sale_data.product_id,
        Product.user_id == current_user.id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get inventory
    inventory = db.query(Inventory).filter(
        Inventory.product_id == sale_data.product_id,
        Inventory.user_id == current_user.id
    ).first()

    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory record not found")

    # Prevent negative stock
    if inventory.quantity_on_hand < sale_data.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    # Reduce stock
    inventory.quantity_on_hand -= sale_data.quantity

    # Create sale
    sale = Sale(
        user_id=current_user.id,
        product_id=sale_data.product_id,
        sale_date=sale_data.sale_date,
        quantity=sale_data.quantity,
        unit_price=sale_data.unit_price,
        total_revenue=sale_data.quantity * sale_data.unit_price,
        customer_id=sale_data.customer_id,
        order_id=sale_data.order_id
    )

    db.add(sale)
    db.commit()
    db.refresh(sale)

    return sale


# ===================== IMPORT CSV =====================
@router.post("/import", response_model=SalesUploadResponse)
async def import_sales_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    contents = await file.read()

    # Detect encoding
    result = chardet.detect(contents)
    encoding = result["encoding"] or "utf-8"

    try:
        df = pd.read_csv(
            io.BytesIO(contents),
            encoding=encoding,
            sep=None,
            engine="python"
        )
    except Exception:
        try:
            df = pd.read_csv(
                io.BytesIO(contents),
                encoding="latin1",
                sep=None,
                engine="python"
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error reading CSV: {str(e)}"
            )

    # Normalize column names
    df.columns = df.columns.str.lower().str.strip()

    # Validate required columns
    required_columns = {"sale_date", "quantity", "unit_price"}
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns: {missing}"
        )

    products = db.query(Product).filter(Product.user_id == current_user.id).all()
    sku_to_id = {p.sku: p.id for p in products}

    imported = 0
    skipped = 0
    errors = []
    sales_to_insert = []

    # FAST iteration
    for row in df.itertuples(index=False):
        try:
            product_id = None

            if "product_id" in df.columns:
                product_id = int(getattr(row, "product_id"))

            elif "sku" in df.columns:
                sku = str(getattr(row, "sku")).strip()
                product_id = sku_to_id.get(sku)

                if not product_id:
                    new_product = Product(
                        user_id=current_user.id,
                        sku=sku,
                        name=sku,
                        unit_price=float(getattr(row, "unit_price", 0))
                    )
                    db.add(new_product)
                    db.flush()
                    product_id = new_product.id
                    sku_to_id[sku] = product_id

            if not product_id:
                skipped += 1
                continue

            sale_date = pd.to_datetime(getattr(row, "sale_date")).date()
            quantity = int(getattr(row, "quantity"))
            unit_price = float(getattr(row, "unit_price"))

            sales_to_insert.append({
                "user_id": current_user.id,
                "product_id": product_id,
                "sale_date": sale_date,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_revenue": quantity * unit_price,
                "customer_id": getattr(row, "customer_id", None),
                "order_id": getattr(row, "order_id", None)
            })

            imported += 1

        except Exception as e:
            skipped += 1
            errors.append(str(e))

    # BULK INSERT (VERY FAST)
    if sales_to_insert:
        db.bulk_insert_mappings(Sale, sales_to_insert)

    db.commit()

    return SalesUploadResponse(
        total_records=len(df),
        imported=imported,
        skipped=skipped,
        errors=errors[:10]
    )


# ===================== SUMMARY =====================
@router.get("/summary")
def get_sales_summary(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from datetime import datetime, timedelta
    from sqlalchemy import func

    start_date = datetime.now().date() - timedelta(days=days)

    sales = db.query(
        func.sum(Sale.quantity).label("total_quantity"),
        func.sum(Sale.total_revenue).label("total_revenue"),
        func.count(Sale.id).label("total_transactions")
    ).filter(
        Sale.user_id == current_user.id,
        Sale.sale_date >= start_date
    ).first()

    return {
        "period_days": days,
        "total_quantity": sales.total_quantity or 0,
        "total_revenue": sales.total_revenue or 0,
        "total_transactions": sales.total_transactions or 0,
        "avg_daily_revenue": (sales.total_revenue or 0) / days
    }
