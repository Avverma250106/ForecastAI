"""
Forecasting router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta

from app.database import get_db
from app.models.forecast import Forecast
from app.models.product import Product
from app.models.sale import Sale
from app.models.user import User
from app.schemas.forecast import ForecastRequest, ForecastResponse, ForecastDataPoint, ForecastSummary
from app.routers.auth import get_current_user

router = APIRouter(prefix="/forecasts", tags=["Forecasts"])


@router.post("/generate/{product_id}", response_model=ForecastResponse)
def generate_forecast(
    product_id: int,
    horizon_days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate demand forecast for a product"""
    from app.services.forecast_service import ForecastService
    
    # Verify product
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Generate forecast
    service = ForecastService(db, current_user.id)
    forecast_data = service.generate_forecast(product_id, horizon_days)
    
    return forecast_data


@router.get("/{product_id}", response_model=ForecastResponse)
def get_forecast(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get existing forecast for a product"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get recent forecasts
    forecasts = db.query(Forecast).filter(
        Forecast.product_id == product_id,
        Forecast.user_id == current_user.id,
        Forecast.forecast_date >= date.today()
    ).order_by(Forecast.forecast_date).all()
    
    if not forecasts:
        raise HTTPException(status_code=404, detail="No forecasts found. Generate a forecast first.")
    
    forecast_data = [
        ForecastDataPoint(
            forecast_date=f.forecast_date,
            predicted_quantity=f.predicted_quantity,
            confidence_lower=f.confidence_lower,
            confidence_upper=f.confidence_upper
        )
        for f in forecasts
    ]
    
    total_demand = sum(f.predicted_quantity for f in forecasts)
    avg_daily = total_demand / len(forecasts) if forecasts else 0
    peak_forecast = max(forecasts, key=lambda x: x.predicted_quantity)
    
    return ForecastResponse(
        product_id=product_id,
        product_name=product.name,
        model_name=forecasts[0].model_name if forecasts else "Unknown",
        generated_at=forecasts[0].generated_at,
        forecast_data=forecast_data,
        total_predicted_demand=total_demand,
        avg_daily_demand=avg_daily,
        peak_date=peak_forecast.forecast_date,
        peak_quantity=peak_forecast.predicted_quantity
    )


@router.get("/", response_model=List[ForecastSummary])
def get_all_forecasts_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get forecast summary for all products"""
    from sqlalchemy import func
    
    products = db.query(Product).filter(Product.user_id == current_user.id).all()
    summaries = []
    
    today = date.today()
    
    for product in products:
        # Get forecasts for different periods
        forecasts_7 = db.query(func.sum(Forecast.predicted_quantity)).filter(
            Forecast.product_id == product.id,
            Forecast.forecast_date >= today,
            Forecast.forecast_date < today + timedelta(days=7)
        ).scalar() or 0
        
        forecasts_30 = db.query(func.sum(Forecast.predicted_quantity)).filter(
            Forecast.product_id == product.id,
            Forecast.forecast_date >= today,
            Forecast.forecast_date < today + timedelta(days=30)
        ).scalar() or 0
        
        forecasts_90 = db.query(func.sum(Forecast.predicted_quantity)).filter(
            Forecast.product_id == product.id,
            Forecast.forecast_date >= today,
            Forecast.forecast_date < today + timedelta(days=90)
        ).scalar() or 0
        
        # Determine trend (simplified)
        if forecasts_30 > 0:
            first_half = forecasts_7
            trend = "increasing" if first_half > forecasts_7 / 2 else "stable"
        else:
            trend = "stable"
        
        summaries.append(ForecastSummary(
            product_id=product.id,
            product_name=product.name,
            next_7_days=forecasts_7,
            next_30_days=forecasts_30,
            next_90_days=forecasts_90,
            trend=trend
        ))
    
    return summaries


@router.post("/generate-all")
def generate_all_forecasts(
    horizon_days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate forecasts for all products"""
    from app.services.forecast_service import ForecastService
    
    products = db.query(Product).filter(Product.user_id == current_user.id).all()
    service = ForecastService(db, current_user.id)
    
    results = {"generated": 0, "failed": 0, "errors": []}
    
    for product in products:
        try:
            service.generate_forecast(product.id, horizon_days)
            results["generated"] += 1
        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"{product.name}: {str(e)}")
    
    return results
