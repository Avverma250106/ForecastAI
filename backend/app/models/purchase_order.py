"""
Purchase Order model
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class POStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    
    # PO details
    po_number = Column(String(50), unique=True, index=True, nullable=False)
    status = Column(String(20), default="draft")
    
    # Dates
    order_date = Column(Date, default=func.current_date())
    expected_delivery_date = Column(Date)
    
    # Totals
    subtotal = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    
    # Notes
    notes = Column(String(1000))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Item details
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="items")
