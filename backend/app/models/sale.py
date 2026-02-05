"""
Sale model for historical transactions
"""
from sqlalchemy import Column, Integer, Float, DateTime, Date, ForeignKey, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Transaction details
    sale_date = Column(Date, index=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_revenue = Column(Float, nullable=False)
    
    # Optional: customer and order reference
    customer_id = Column(String(100))
    order_id = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="sales")
