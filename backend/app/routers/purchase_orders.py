"""
Purchase Orders router
"""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime
import uuid

from app.database import get_db
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.user import User
from app.schemas.purchase_order import POCreate, POResponse, POItemResponse, POStatusUpdate, POGenerateRequest
from app.routers.auth import get_current_user

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])


def generate_po_number():
    """Generate unique PO number"""
    return f"PO-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


@router.get("/", response_model=List[POResponse])
def get_purchase_orders(
    status: str = None,
    supplier_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all purchase orders"""
    query = db.query(PurchaseOrder).filter(PurchaseOrder.user_id == current_user.id)
    
    if status:
        query = query.filter(PurchaseOrder.status == status)
    if supplier_id:
        query = query.filter(PurchaseOrder.supplier_id == supplier_id)
    
    orders = query.order_by(PurchaseOrder.created_at.desc()).all()
    
    result = []
    for order in orders:
        supplier = db.query(Supplier).filter(Supplier.id == order.supplier_id).first()
        items = []
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            items.append(POItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=product.name if product else "Unknown",
                product_sku=product.sku if product else "Unknown",
                quantity=item.quantity,
                unit_cost=item.unit_cost,
                total_cost=item.total_cost
            ))
        
        result.append(POResponse(
            id=order.id,
            po_number=order.po_number,
            supplier_id=order.supplier_id,
            supplier_name=supplier.name if supplier else "Unknown",
            status=order.status,
            order_date=order.order_date,
            expected_delivery_date=order.expected_delivery_date,
            subtotal=order.subtotal,
            tax=order.tax,
            total=order.total,
            notes=order.notes,
            items=items,
            created_at=order.created_at
        ))
    
    return result


@router.get("/{po_id}", response_model=POResponse)
def get_purchase_order(
    po_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific purchase order"""
    order = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == po_id,
        PurchaseOrder.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    supplier = db.query(Supplier).filter(Supplier.id == order.supplier_id).first()
    items = []
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        items.append(POItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_name=product.name if product else "Unknown",
            product_sku=product.sku if product else "Unknown",
            quantity=item.quantity,
            unit_cost=item.unit_cost,
            total_cost=item.total_cost
        ))
    
    return POResponse(
        id=order.id,
        po_number=order.po_number,
        supplier_id=order.supplier_id,
        supplier_name=supplier.name if supplier else "Unknown",
        status=order.status,
        order_date=order.order_date,
        expected_delivery_date=order.expected_delivery_date,
        subtotal=order.subtotal,
        tax=order.tax,
        total=order.total,
        notes=order.notes,
        items=items,
        created_at=order.created_at
    )


@router.post("/", response_model=POResponse)
def create_purchase_order(
    po_data: POCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new purchase order"""
    # Verify supplier
    supplier = db.query(Supplier).filter(
        Supplier.id == po_data.supplier_id,
        Supplier.user_id == current_user.id
    ).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    # Create PO
    po = PurchaseOrder(
        user_id=current_user.id,
        supplier_id=po_data.supplier_id,
        po_number=generate_po_number(),
        status="draft",
        expected_delivery_date=po_data.expected_delivery_date,
        notes=po_data.notes
    )
    db.add(po)
    db.flush()
    
    # Add items
    subtotal = 0
    items = []
    for item_data in po_data.items:
        product = db.query(Product).filter(
            Product.id == item_data.product_id,
            Product.user_id == current_user.id
        ).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item_data.product_id} not found")
        
        total_cost = item_data.quantity * product.unit_cost
        subtotal += total_cost
        
        item = PurchaseOrderItem(
            purchase_order_id=po.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            unit_cost=product.unit_cost,
            total_cost=total_cost
        )
        db.add(item)
        items.append(POItemResponse(
            id=0,
            product_id=product.id,
            product_name=product.name,
            product_sku=product.sku,
            quantity=item_data.quantity,
            unit_cost=product.unit_cost,
            total_cost=total_cost
        ))
    
    # Update totals
    po.subtotal = subtotal
    po.tax = 0  # Can be configured later
    po.total = subtotal
    
    db.commit()
    db.refresh(po)
    
    return POResponse(
        id=po.id,
        po_number=po.po_number,
        supplier_id=po.supplier_id,
        supplier_name=supplier.name,
        status=po.status,
        order_date=po.order_date,
        expected_delivery_date=po.expected_delivery_date,
        subtotal=po.subtotal,
        tax=po.tax,
        total=po.total,
        notes=po.notes,
        items=items,
        created_at=po.created_at
    )


@router.put("/{po_id}/status")
def update_po_status(
    po_id: int,
    status_data: POStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update purchase order status"""
    po = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == po_id,
        PurchaseOrder.user_id == current_user.id
    ).first()
    
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    valid_statuses = ["draft", "sent", "confirmed", "shipped", "received", "cancelled"]
    if status_data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    po.status = status_data.status
    db.commit()
    
    return {"message": f"PO status updated to {status_data.status}"}


@router.get("/{po_id}/pdf")
def download_po_pdf(
    po_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate and download PO as PDF"""
    from app.services.po_service import POService
    
    po = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == po_id,
        PurchaseOrder.user_id == current_user.id
    ).first()
    
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    service = POService(db, current_user.id)
    pdf_bytes = service.generate_pdf(po_id)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={po.po_number}.pdf"}
    )


@router.delete("/{po_id}")
def delete_purchase_order(
    po_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a purchase order"""
    po = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == po_id,
        PurchaseOrder.user_id == current_user.id
    ).first()
    
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    
    if po.status not in ["draft", "cancelled"]:
        raise HTTPException(status_code=400, detail="Can only delete draft or cancelled orders")
    
    db.delete(po)
    db.commit()
    return {"message": "Purchase order deleted successfully"}
