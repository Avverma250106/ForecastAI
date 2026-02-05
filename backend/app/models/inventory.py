"""
Inventory model for current stock levels
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True, nullable=False)
    
    # Stock levels
    quantity_on_hand = Column(Integer, default=0)
    quantity_reserved = Column(Integer, default=0)  # Reserved for orders
    quantity_on_order = Column(Integer, default=0)  # Currently ordered from supplier
    
    # Location (optional)
    warehouse_location = Column(Integer, default=1)
    
    # Timestamps
    last_stock_update = Column(DateTime(timezone=True), server_default=func.now())
    last_count_date = Column(DateTime(timezone=True))
    
    # Relationships
    product = relationship("Product", back_populates="inventory")
    
    @property
    def available_quantity(self):
        """Get available stock (on hand minus reserved)"""
        return self.quantity_on_hand - self.quantity_reserved
