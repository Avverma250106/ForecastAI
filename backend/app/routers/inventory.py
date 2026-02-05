"""
Inventory router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.user import User
from app.schemas.inventory import InventoryUpdate, InventoryResponse, InventoryHealth
from app.routers.auth import get_current_user

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("/", response_model=List[dict])
def get_inventory(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all inventory with product details"""
    inventory_items = db.query(Inventory, Product).join(
        Product, Inventory.product_id == Product.id
    ).filter(
        Inventory.user_id == current_user.id
    ).all()
    
    result = []
    for inv, product in inventory_items:
        result.append({
            "id": inv.id,
            "product_id": product.id,
            "product_sku": product.sku,
            "product_name": product.name,
            "category": product.category,
            "quantity_on_hand": inv.quantity_on_hand,
            "quantity_reserved": inv.quantity_reserved,
            "quantity_on_order": inv.quantity_on_order,
            "available_quantity": inv.quantity_on_hand - inv.quantity_reserved,
            "reorder_point": product.reorder_point,
            "safety_stock": product.safety_stock,
            "last_stock_update": inv.last_stock_update
        })
    
    return result


@router.get("/{product_id}")
def get_product_inventory(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get inventory for a specific product"""
    inventory = db.query(Inventory).filter(
        Inventory.product_id == product_id,
        Inventory.user_id == current_user.id
    ).first()
    
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    product = db.query(Product).filter(Product.id == product_id).first()
    
    return {
        "id": inventory.id,
        "product_id": product_id,
        "product_name": product.name,
        "quantity_on_hand": inventory.quantity_on_hand,
        "quantity_reserved": inventory.quantity_reserved,
        "quantity_on_order": inventory.quantity_on_order,
        "available_quantity": inventory.quantity_on_hand - inventory.quantity_reserved,
        "last_stock_update": inventory.last_stock_update
    }


@router.put("/{product_id}")
def update_inventory(
    product_id: int,
    inventory_data: InventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update inventory for a product"""
    inventory = db.query(Inventory).filter(
        Inventory.product_id == product_id,
        Inventory.user_id == current_user.id
    ).first()
    
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    update_data = inventory_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(inventory, key, value)
    
    from datetime import datetime
    inventory.last_stock_update = datetime.utcnow()
    
    db.commit()
    db.refresh(inventory)
    
    return {"message": "Inventory updated successfully", "inventory": inventory}


@router.get("/health/summary", response_model=InventoryHealth)
def get_inventory_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overall inventory health metrics"""
    inventory_items = db.query(Inventory, Product).join(
        Product, Inventory.product_id == Product.id
    ).filter(
        Inventory.user_id == current_user.id
    ).all()
    
    total = len(inventory_items)
    healthy = 0
    low_stock = 0
    out_of_stock = 0
    overstocked = 0
    
    for inv, product in inventory_items:
        available = inv.quantity_on_hand - inv.quantity_reserved
        
        if available <= 0:
            out_of_stock += 1
        elif available <= product.reorder_point:
            low_stock += 1
        elif available > product.reorder_point * 3:  # Arbitrary overstock threshold
            overstocked += 1
        else:
            healthy += 1
    
    # Calculate health score (0-100)
    if total > 0:
        health_score = ((healthy + overstocked * 0.8) / total) * 100
    else:
        health_score = 100.0
    
    return InventoryHealth(
        total_products=total,
        healthy_stock=healthy,
        low_stock=low_stock,
        out_of_stock=out_of_stock,
        overstocked=overstocked,
        health_score=round(health_score, 1)
    )
