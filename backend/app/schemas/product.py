"""
Product schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ProductBase(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    unit_cost: float = 0.0
    unit_price: float = 0.0
    reorder_point: int = 10
    safety_stock: int = 5


class ProductCreate(ProductBase):
    supplier_id: Optional[int] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    unit_cost: Optional[float] = None
    unit_price: Optional[float] = None
    reorder_point: Optional[int] = None
    safety_stock: Optional[int] = None
    supplier_id: Optional[int] = None


class ProductResponse(ProductBase):
    id: int
    user_id: int
    supplier_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProductWithInventory(ProductResponse):
    current_stock: int = 0
    days_of_stock: Optional[float] = None
