"""
Product model for SKU catalog
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    
    # Product info
    sku = Column(String(100), index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    category = Column(String(100))
    
    # Pricing
    unit_cost = Column(Float, default=0.0)  # Cost price
    unit_price = Column(Float, default=0.0)  # Selling price
    
    # Inventory settings
    reorder_point = Column(Integer, default=10)  # Min stock before reorder
    safety_stock = Column(Integer, default=5)  # Buffer stock
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    supplier = relationship("Supplier", back_populates="products")
    sales = relationship("Sale", back_populates="product")
    inventory = relationship("Inventory",back_populates="product",cascade="all, delete",passive_deletes=True)
    forecasts = relationship(
    "Forecast",
    back_populates="product",
    cascade="all, delete-orphan",
    passive_deletes=True
    )

    alerts = relationship("Alert", back_populates="product")
