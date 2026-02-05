"""
Inventory schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class InventoryUpdate(BaseModel):
    quantity_on_hand: Optional[int] = None
    quantity_reserved: Optional[int] = None
    quantity_on_order: Optional[int] = None


class InventoryResponse(BaseModel):
    id: int
    product_id: int
    quantity_on_hand: int
    quantity_reserved: int
    quantity_on_order: int
    available_quantity: int
    last_stock_update: datetime
    
    class Config:
        from_attributes = True


class InventoryHealth(BaseModel):
    """Overall inventory health metrics"""
    total_products: int
    healthy_stock: int
    low_stock: int
    out_of_stock: int
    overstocked: int
    health_score: float  # 0-100 score
