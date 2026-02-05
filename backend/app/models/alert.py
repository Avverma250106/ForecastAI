"""
Alert model for notifications
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class AlertType(str, enum.Enum):
    STOCKOUT_WARNING = "stockout_warning"
    LOW_STOCK = "low_stock"
    REORDER_REMINDER = "reorder_reminder"
    OVERSTOCK = "overstock"


class AlertPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Alert details
    alert_type = Column(String(50), nullable=False)
    priority = Column(String(20), default="medium")
    title = Column(String(255), nullable=False)
    message = Column(String(1000))
    
    # Recommendations
    recommended_action = Column(String(500))
    recommended_quantity = Column(Integer)
    
    # Status
    is_read = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    
    # Relationships
    product = relationship("Product", back_populates="alerts")
