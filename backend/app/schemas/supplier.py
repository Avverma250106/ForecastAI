"""
Supplier schemas
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class SupplierBase(BaseModel):
    name: str
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    lead_time_days: int = 7
    minimum_order_quantity: int = 1


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    lead_time_days: Optional[int] = None
    minimum_order_quantity: Optional[int] = None


class SupplierResponse(SupplierBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
