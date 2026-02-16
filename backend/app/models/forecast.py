"""
Forecast model for demand predictions
"""
from sqlalchemy import Column, Integer, Float, DateTime, Date, ForeignKey, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Forecast(Base):
    __tablename__ = "forecasts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(
    Integer,
    ForeignKey("products.id", ondelete="CASCADE"),
    nullable=False
)

    
    # Forecast details
    forecast_date = Column(Date, index=True, nullable=False)  # Date being predicted
    predicted_quantity = Column(Float, nullable=False)
    confidence_lower = Column(Float)  # Lower bound of confidence interval
    confidence_upper = Column(Float)  # Upper bound of confidence interval
    confidence_level = Column(Float, default=0.95)  # 95% confidence
    
    # Model info
    model_name = Column(String(50), default="RandomForest")
    model_version = Column(String(20))
    
    # Timestamps
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="forecasts")

