"""
Alerts router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.alert import Alert
from app.models.product import Product
from app.models.user import User
from app.schemas.alert import AlertResponse, AlertUpdate, AlertSummary
from app.routers.auth import get_current_user

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/", response_model=List[AlertResponse])
def get_alerts(
    priority: str = None,
    is_resolved: bool = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all alerts with optional filters"""
    query = db.query(Alert, Product).join(
        Product, Alert.product_id == Product.id
    ).filter(Alert.user_id == current_user.id)
    
    if priority:
        query = query.filter(Alert.priority == priority)
    if is_resolved is not None:
        query = query.filter(Alert.is_resolved == is_resolved)
    
    results = query.order_by(
        Alert.is_resolved,
        Alert.priority.desc(),
        Alert.created_at.desc()
    ).limit(limit).all()
    
    return [
        AlertResponse(
            id=alert.id,
            product_id=alert.product_id,
            product_name=product.name,
            alert_type=alert.alert_type,
            priority=alert.priority,
            title=alert.title,
            message=alert.message,
            recommended_action=alert.recommended_action,
            recommended_quantity=alert.recommended_quantity,
            is_read=alert.is_read,
            is_resolved=alert.is_resolved,
            created_at=alert.created_at
        )
        for alert, product in results
    ]


@router.get("/summary", response_model=AlertSummary)
def get_alerts_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get alerts summary for dashboard"""
    from sqlalchemy import func
    
    # Active alerts only
    alerts = db.query(Alert).filter(
        Alert.user_id == current_user.id,
        Alert.is_resolved == False
    ).all()
    
    summary = {
        "total_alerts": len(alerts),
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "unread": 0
    }
    
    for alert in alerts:
        priority = alert.priority.lower()
        if priority in summary:
            summary[priority] += 1
        if not alert.is_read:
            summary["unread"] += 1
    
    return AlertSummary(**summary)


@router.put("/{alert_id}")
def update_alert(
    alert_id: int,
    alert_data: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update alert status"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if alert_data.is_read is not None:
        alert.is_read = alert_data.is_read
    if alert_data.is_resolved is not None:
        alert.is_resolved = alert_data.is_resolved
        if alert_data.is_resolved:
            alert.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(alert)
    return {"message": "Alert updated successfully"}


@router.post("/{alert_id}/resolve")
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark alert as resolved"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Alert resolved successfully"}


@router.post("/generate")
def generate_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate alerts based on current inventory and forecasts"""
    from app.services.alert_service import AlertService
    
    service = AlertService(db, current_user.id)
    results = service.generate_alerts()
    
    return results


@router.delete("/{alert_id}")
def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an alert"""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    db.delete(alert)
    db.commit()
    return {"message": "Alert deleted successfully"}
