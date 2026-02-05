"""
Sales router with CSV import
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import date
import pandas as pd
import io

from app.database import get_db
from app.models.sale import Sale
from app.models.product import Product
from app.models.user import User
from app.schemas.sale import SaleCreate, SaleResponse, SalesUploadResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/sales", tags=["Sales"])


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
    """Get sales with optional filters"""
    query = db.query(Sale).filter(Sale.user_id == current_user.id)
    
    if product_id:
        query = query.filter(Sale.product_id == product_id)
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    
    return query.order_by(Sale.sale_date.desc()).offset(skip).limit(limit).all()


@router.post("/", response_model=SaleResponse)
def create_sale(
    sale_data: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a single sale record"""
    # Verify product exists
    product = db.query(Product).filter(
        Product.id == sale_data.product_id,
        Product.user_id == current_user.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
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


@router.post("/import", response_model=SalesUploadResponse)
async def import_sales_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Import sales data from CSV file.
    
    Expected columns:
    - sku (or product_id): Product identifier
    - sale_date: Date of sale (YYYY-MM-DD)
    - quantity: Quantity sold
    - unit_price: Price per unit
    - customer_id (optional)
    - order_id (optional)
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    contents = await file.read()
    
    try:
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV: {str(e)}")
    
    # Normalize column names
    df.columns = df.columns.str.lower().str.strip()
    
    # Get user's products for SKU lookup
    products = db.query(Product).filter(Product.user_id == current_user.id).all()
    sku_to_id = {p.sku: p.id for p in products}
    
    imported = 0
    skipped = 0
    errors = []
    
    for idx, row in df.iterrows():
        try:
            # Get product ID
            product_id = None
            if 'product_id' in df.columns:
                product_id = int(row['product_id'])
            elif 'sku' in df.columns:
                sku = str(row['sku']).strip()
                product_id = sku_to_id.get(sku)
                if not product_id:
                    # Auto-create product if not exists
                    new_product = Product(
                        user_id=current_user.id,
                        sku=sku,
                        name=sku,
                        unit_price=float(row.get('unit_price', 0))
                    )
                    db.add(new_product)
                    db.flush()
                    product_id = new_product.id
                    sku_to_id[sku] = product_id
            
            if not product_id:
                skipped += 1
                errors.append(f"Row {idx+1}: No valid product identifier")
                continue
            
            # Parse date
            sale_date = pd.to_datetime(row['sale_date']).date()
            quantity = int(row['quantity'])
            unit_price = float(row['unit_price'])
            
            # Create sale
            sale = Sale(
                user_id=current_user.id,
                product_id=product_id,
                sale_date=sale_date,
                quantity=quantity,
                unit_price=unit_price,
                total_revenue=quantity * unit_price,
                customer_id=str(row.get('customer_id', '')) if pd.notna(row.get('customer_id')) else None,
                order_id=str(row.get('order_id', '')) if pd.notna(row.get('order_id')) else None
            )
            db.add(sale)
            imported += 1
            
        except Exception as e:
            skipped += 1
            errors.append(f"Row {idx+1}: {str(e)}")
    
    db.commit()
    
    return SalesUploadResponse(
        total_records=len(df),
        imported=imported,
        skipped=skipped,
        errors=errors[:10]  # Return first 10 errors only
    )


@router.get("/summary")
def get_sales_summary(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get sales summary for last N days"""
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    start_date = datetime.now().date() - timedelta(days=days)
    
    sales = db.query(
        func.sum(Sale.quantity).label('total_quantity'),
        func.sum(Sale.total_revenue).label('total_revenue'),
        func.count(Sale.id).label('total_transactions')
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
