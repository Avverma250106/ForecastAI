"""
Sale schemas
"""
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List


class SaleBase(BaseModel):
    product_id: int
    sale_date: date
    quantity: int
    unit_price: float


class SaleCreate(SaleBase):
    customer_id: Optional[str] = None
    order_id: Optional[str] = None


class SaleResponse(SaleBase):
    id: int
    user_id: int
    total_revenue: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class SaleImport(BaseModel):
    """Schema for CSV import"""
    sku: str
    sale_date: date
    quantity: int
    unit_price: float
    customer_id: Optional[str] = None
    order_id: Optional[str] = None


class SalesUploadResponse(BaseModel):
    total_records: int
    imported: int
    skipped: int
    errors: List[str]
