"""
Forecast schemas
"""
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List


class ForecastRequest(BaseModel):
    product_id: int
    horizon_days: int = 30  # Default 30-day forecast


class ForecastDataPoint(BaseModel):
    forecast_date: date
    predicted_quantity: float
    confidence_lower: Optional[float] = None
    confidence_upper: Optional[float] = None


class ForecastResponse(BaseModel):
    product_id: int
    product_name: str
    model_name: str
    generated_at: datetime
    forecast_data: List[ForecastDataPoint]
    
    # Summary statistics
    total_predicted_demand: float
    avg_daily_demand: float
    peak_date: date
    peak_quantity: float


class ForecastSummary(BaseModel):
    """Quick summary for dashboard"""
    product_id: int
    product_name: str
    next_7_days: float
    next_30_days: float
    next_90_days: float
    trend: str  # "increasing", "decreasing", "stable"
