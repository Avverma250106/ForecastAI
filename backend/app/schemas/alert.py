"""
Alert schemas
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class AlertResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    alert_type: str
    priority: str
    title: str
    message: Optional[str]
    recommended_action: Optional[str]
    recommended_quantity: Optional[int]
    is_read: bool
    is_resolved: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_resolved: Optional[bool] = None


class AlertSummary(BaseModel):
    """Dashboard summary"""
    total_alerts: int
    critical: int
    high: int
    medium: int
    low: int
    unread: int
