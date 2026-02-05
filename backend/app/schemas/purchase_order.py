"""
Purchase Order schemas
"""
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List


class POItemCreate(BaseModel):
    product_id: int
    quantity: int


class POItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_sku: str
    quantity: int
    unit_cost: float
    total_cost: float
    
    class Config:
        from_attributes = True


class POCreate(BaseModel):
    supplier_id: int
    items: List[POItemCreate]
    expected_delivery_date: Optional[date] = None
    notes: Optional[str] = None


class POResponse(BaseModel):
    id: int
    po_number: str
    supplier_id: int
    supplier_name: str
    status: str
    order_date: date
    expected_delivery_date: Optional[date]
    subtotal: float
    tax: float
    total: float
    notes: Optional[str]
    items: List[POItemResponse]
    created_at: datetime
    
    class Config:
        from_attributes = True


class POStatusUpdate(BaseModel):
    status: str


class POGenerateRequest(BaseModel):
    """Auto-generate PO from recommendations"""
    product_ids: List[int]
