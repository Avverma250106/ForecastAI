"""
Dashboard router - aggregated data for UI
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta, datetime

from app.database import get_db
from app.models.sale import Sale
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.alert import Alert
from app.models.forecast import Forecast
from app.models.user import User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview")
def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get main dashboard metrics"""
    today = date.today()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)
    
    # Product count
    total_products = db.query(func.count(Product.id)).filter(
        Product.user_id == current_user.id
    ).scalar() or 0
    
    # Sales metrics (last 30 days)
    sales_30d = db.query(
        func.sum(Sale.total_revenue).label('revenue'),
        func.sum(Sale.quantity).label('quantity')
    ).filter(
        Sale.user_id == current_user.id,
        Sale.sale_date >= last_30_days
    ).first()
    
    # Sales metrics (last 7 days)
    sales_7d = db.query(
        func.sum(Sale.total_revenue).label('revenue'),
        func.sum(Sale.quantity).label('quantity')
    ).filter(
        Sale.user_id == current_user.id,
        Sale.sale_date >= last_7_days
    ).first()
    
    # Inventory health
    inventory_items = db.query(Inventory, Product).join(
        Product, Inventory.product_id == Product.id
    ).filter(
        Inventory.user_id == current_user.id
    ).all()
    
    out_of_stock = 0
    low_stock = 0
    for inv, product in inventory_items:
        available = inv.quantity_on_hand - inv.quantity_reserved
        if available <= 0:
            out_of_stock += 1
        elif available <= product.reorder_point:
            low_stock += 1
    
    # Active alerts
    active_alerts = db.query(func.count(Alert.id)).filter(
        Alert.user_id == current_user.id,
        Alert.is_resolved == False
    ).scalar() or 0
    
    critical_alerts = db.query(func.count(Alert.id)).filter(
        Alert.user_id == current_user.id,
        Alert.is_resolved == False,
        Alert.priority == "critical"
    ).scalar() or 0
    
    # Calculate inventory health score
    total_inventory = len(inventory_items)
    if total_inventory > 0:
        health_score = ((total_inventory - out_of_stock - low_stock) / total_inventory) * 100
    else:
        health_score = 100.0
    
    return {
        "total_products": total_products,
        "revenue_30d": sales_30d.revenue or 0,
        "revenue_7d": sales_7d.revenue or 0,
        "units_sold_30d": sales_30d.quantity or 0,
        "units_sold_7d": sales_7d.quantity or 0,
        "out_of_stock_count": out_of_stock,
        "low_stock_count": low_stock,
        "active_alerts": active_alerts,
        "critical_alerts": critical_alerts,
        "inventory_health_score": round(health_score, 1)
    }


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard stats (alias for overview)"""
    return get_dashboard_overview(db, current_user)


@router.get("/sales-chart")
def get_sales_chart_data(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get daily sales data for chart"""
    start_date = date.today() - timedelta(days=days)
    
    sales = db.query(
        Sale.sale_date,
        func.sum(Sale.total_revenue).label('revenue'),
        func.sum(Sale.quantity).label('quantity')
    ).filter(
        Sale.user_id == current_user.id,
        Sale.sale_date >= start_date
    ).group_by(Sale.sale_date).order_by(Sale.sale_date).all()
    
    return [
        {
            "date": s.sale_date.isoformat(),
            "revenue": s.revenue or 0,
            "quantity": s.quantity or 0
        }
        for s in sales
    ]


@router.get("/top-products")
def get_top_products(
    limit: int = 10,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get top selling products"""
    start_date = date.today() - timedelta(days=days)
    
    top_products = db.query(
        Product.id,
        Product.name,
        Product.sku,
        func.sum(Sale.quantity).label('total_quantity'),
        func.sum(Sale.total_revenue).label('total_revenue')
    ).join(
        Sale, Sale.product_id == Product.id
    ).filter(
        Product.user_id == current_user.id,
        Sale.sale_date >= start_date
    ).group_by(
        Product.id, Product.name, Product.sku
    ).order_by(
        func.sum(Sale.total_revenue).desc()
    ).limit(limit).all()
    
    return [
        {
            "product_id": p.id,
            "product_name": p.name,
            "sku": p.sku,
            "total_quantity": p.total_quantity or 0,
            "total_revenue": p.total_revenue or 0
        }
        for p in top_products
    ]


@router.get("/alerts-preview")
def get_alerts_preview(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recent urgent alerts for dashboard preview"""
    alerts = db.query(Alert, Product).join(
        Product, Alert.product_id == Product.id
    ).filter(
        Alert.user_id == current_user.id,
        Alert.is_resolved == False
    ).order_by(
        Alert.priority.desc(),
        Alert.created_at.desc()
    ).limit(limit).all()
    
    return [
        {
            "id": alert.id,
            "product_name": product.name,
            "alert_type": alert.alert_type,
            "priority": alert.priority,
            "title": alert.title,
            "created_at": alert.created_at.isoformat()
        }
        for alert, product in alerts
    ]


@router.get("/forecast-preview")
def get_forecast_preview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get forecast summary for next 7 days"""
    today = date.today()
    next_7_days = today + timedelta(days=7)
    
    # Get products with low stock that need attention
    inventory_items = db.query(Inventory, Product).join(
        Product, Inventory.product_id == Product.id
    ).filter(
        Inventory.user_id == current_user.id
    ).all()
    
    preview = []
    for inv, product in inventory_items:
        # Get forecast for next 7 days
        forecast_sum = db.query(func.sum(Forecast.predicted_quantity)).filter(
            Forecast.product_id == product.id,
            Forecast.forecast_date >= today,
            Forecast.forecast_date < next_7_days
        ).scalar() or 0
        
        available = inv.quantity_on_hand - inv.quantity_reserved
        days_of_stock = available / (forecast_sum / 7) if forecast_sum > 0 else 999
        
        if days_of_stock < 14:  # Show products running low
            preview.append({
                "product_id": product.id,
                "product_name": product.name,
                "current_stock": available,
                "forecast_7d": round(forecast_sum, 1),
                "days_of_stock": round(days_of_stock, 1)
            })
    
    # Sort by days of stock (ascending)
    preview.sort(key=lambda x: x["days_of_stock"])
    
    return preview[:10]  # Return top 10 needing attention


@router.get("/alerts")
def get_alerts_for_dashboard(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get alerts for dashboard (alias for alerts-preview)"""
    return get_alerts_preview(limit, db, current_user)


@router.get("/inventory-health")
def get_inventory_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get inventory health breakdown for pie chart"""
    inventory_items = db.query(Inventory, Product).join(
        Product, Inventory.product_id == Product.id
    ).filter(
        Inventory.user_id == current_user.id
    ).all()
    
    healthy = 0
    low_stock = 0
    critical = 0
    out_of_stock = 0
    
    for inv, product in inventory_items:
        available = inv.quantity_on_hand - inv.quantity_reserved
        if available <= 0:
            out_of_stock += 1
        elif available <= product.reorder_point * 0.5:
            critical += 1
        elif available <= product.reorder_point:
            low_stock += 1
        else:
            healthy += 1
    
    return {
        "healthy": healthy,
        "low_stock": low_stock,
        "critical": critical,
        "out_of_stock": out_of_stock,
        "total": len(inventory_items)
    }
