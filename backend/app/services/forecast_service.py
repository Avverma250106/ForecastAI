"""
Forecasting Service - ML-powered demand prediction
"""
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
import joblib
import os

from app.models.sale import Sale
from app.models.product import Product
from app.models.forecast import Forecast
from app.schemas.forecast import ForecastResponse, ForecastDataPoint
from app.config import settings


class ForecastService:
  
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self.model = None
        self.model_name = "RandomForest"
    
    def _get_sales_data(self, product_id: int) -> pd.DataFrame:
        """Fetch historical sales data for a product"""
        sales = self.db.query(Sale).filter(
            Sale.user_id == self.user_id,
            Sale.product_id == product_id
        ).order_by(Sale.sale_date).all()
        
        if not sales:
            return pd.DataFrame()
        
        data = [{
            'sale_date': s.sale_date,
            'quantity': s.quantity,
            'unit_price': s.unit_price,
            'revenue': s.total_revenue
        } for s in sales]
        
        df = pd.DataFrame(data)
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        return df
    
    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create features for ML model"""
        if df.empty:
            return df
        
        # Aggregate to daily level
        daily = df.groupby('sale_date').agg({
            'quantity': 'sum',
            'revenue': 'sum'
        }).reset_index()
        
        # Create date range to fill missing dates
        date_range = pd.date_range(
            start=daily['sale_date'].min(),
            end=daily['sale_date'].max(),
            freq='D'
        )
        daily = daily.set_index('sale_date').reindex(date_range, fill_value=0).reset_index()
        daily.columns = ['sale_date', 'quantity', 'revenue']
        
        # Time-based features
        daily['day_of_week'] = daily['sale_date'].dt.dayofweek
        daily['day_of_month'] = daily['sale_date'].dt.day
        daily['month'] = daily['sale_date'].dt.month
        daily['week_of_year'] = daily['sale_date'].dt.isocalendar().week.astype(int)
        daily['is_weekend'] = (daily['day_of_week'] >= 5).astype(int)
        
        # Lag features
        for lag in [1, 7, 14, 30]:
            daily[f'lag_{lag}'] = daily['quantity'].shift(lag)
        
        # Rolling averages
        for window in [7, 14, 30]:
            daily[f'rolling_mean_{window}'] = daily['quantity'].rolling(window=window, min_periods=1).mean()
            daily[f'rolling_std_{window}'] = daily['quantity'].rolling(window=window, min_periods=1).std()
        
        # Fill NaN values
        daily = daily.fillna(0)
        
        return daily
    
    from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_percentage_error

def _train_model(self, df: pd.DataFrame):
    from sklearn.ensemble import RandomForestRegressor
    
    feature_cols = [
        'day_of_week', 'day_of_month', 'month', 'week_of_year', 'is_weekend',
        'lag_1', 'lag_7', 'lag_14', 'lag_30',
        'rolling_mean_7', 'rolling_mean_14', 'rolling_mean_30',
        'rolling_std_7', 'rolling_std_14', 'rolling_std_30'
    ]

    X = df[feature_cols]
    y = df['quantity']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    self.model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        random_state=42,
        n_jobs=-1
    )

    self.model.fit(X_train, y_train)

    # Evaluate model
    y_pred = self.model.predict(X_test)

    r2 = r2_score(y_test, y_pred)
    mape = mean_absolute_percentage_error(y_test, y_pred)

    self.model_accuracy = round((1 - mape) * 100, 2)
    self.r2_score = round(r2 * 100, 2)

    
    def _make_predictions(self, df: pd.DataFrame, horizon_days: int) -> List[Dict]:
        """Generate predictions for future dates"""
        predictions = []
        
        # Get last known data for features
        last_date = df['sale_date'].max()
        recent_data = df.tail(30).copy()
        
        feature_cols = [
            'day_of_week', 'day_of_month', 'month', 'week_of_year', 'is_weekend',
            'lag_1', 'lag_7', 'lag_14', 'lag_30',
            'rolling_mean_7', 'rolling_mean_14', 'rolling_mean_30',
            'rolling_std_7', 'rolling_std_14', 'rolling_std_30'
        ]
        
        for i in range(1, horizon_days + 1):
            future_date = last_date + timedelta(days=i)
            
            # Create features for future date
            features = {
                'day_of_week': future_date.dayofweek,
                'day_of_month': future_date.day,
                'month': future_date.month,
                'week_of_year': future_date.isocalendar()[1],
                'is_weekend': 1 if future_date.dayofweek >= 5 else 0,
            }
            
            # Use recent predictions for lag features
            quantities = list(recent_data['quantity'].tail(30))
            if len(predictions) > 0:
                quantities = quantities[len(predictions):] + [p['predicted_quantity'] for p in predictions]
            
            features['lag_1'] = quantities[-1] if len(quantities) >= 1 else 0
            features['lag_7'] = quantities[-7] if len(quantities) >= 7 else 0
            features['lag_14'] = quantities[-14] if len(quantities) >= 14 else 0
            features['lag_30'] = quantities[-30] if len(quantities) >= 30 else 0
            
            # Rolling features from recent data + predictions
            recent_qty = quantities[-7:] if len(quantities) >= 7 else quantities
            features['rolling_mean_7'] = np.mean(recent_qty)
            features['rolling_std_7'] = np.std(recent_qty) if len(recent_qty) > 1 else 0
            
            recent_qty_14 = quantities[-14:] if len(quantities) >= 14 else quantities
            features['rolling_mean_14'] = np.mean(recent_qty_14)
            features['rolling_std_14'] = np.std(recent_qty_14) if len(recent_qty_14) > 1 else 0
            
            recent_qty_30 = quantities[-30:] if len(quantities) >= 30 else quantities
            features['rolling_mean_30'] = np.mean(recent_qty_30)
            features['rolling_std_30'] = np.std(recent_qty_30) if len(recent_qty_30) > 1 else 0
            
            # Make prediction
            X_pred = pd.DataFrame([features])[feature_cols]
            pred = self.model.predict(X_pred)[0]
            pred = max(0, pred)  # No negative predictions
            
            # Estimate confidence interval (simplified)
            std = features['rolling_std_30']
            confidence_lower = max(0, pred - 1.96 * std)
            confidence_upper = pred + 1.96 * std
            
            predictions.append({
                'forecast_date': future_date.date(),
                'predicted_quantity': round(pred, 2),
                'confidence_lower': round(confidence_lower, 2),
                'confidence_upper': round(confidence_upper, 2)
            })
        
        return predictions
    
    def generate_forecast(self, product_id: int, horizon_days: int = 30) -> ForecastResponse:
        """Generate demand forecast for a product"""
        # Get product info
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        # Get and prepare data
        df = self._get_sales_data(product_id)
        
        if df.empty or len(df) < 7:
            # Not enough data - use simple average
            avg_qty = df['quantity'].mean() if not df.empty else 1.0
            predictions = []
            for i in range(1, horizon_days + 1):
                future_date = date.today() + timedelta(days=i)
                predictions.append({
                    'forecast_date': future_date,
                    'predicted_quantity': round(avg_qty, 2),
                    'confidence_lower': round(max(0, avg_qty * 0.5), 2),
                    'confidence_upper': round(avg_qty * 1.5, 2)
                })
        else:
            # Create features and train model
            feature_df = self._create_features(df)
            self._train_model(feature_df)
            predictions = self._make_predictions(feature_df, horizon_days)
        
        # Save forecasts to database
        self._save_forecasts(product_id, predictions)
        
        # Build response
        forecast_data = [
            ForecastDataPoint(
                forecast_date=p['forecast_date'],
                predicted_quantity=p['predicted_quantity'],
                confidence_lower=p['confidence_lower'],
                confidence_upper=p['confidence_upper']
            )
            for p in predictions
        ]
        
        total_demand = sum(p['predicted_quantity'] for p in predictions)
        avg_daily = total_demand / len(predictions) if predictions else 0
        peak = max(predictions, key=lambda x: x['predicted_quantity'])
        
        return ForecastResponse(
            product_id=product_id,
            product_name=product.name,
            model_name=self.model_name,
            generated_at=datetime.utcnow(),
            forecast_data=forecast_data,
            total_predicted_demand=round(total_demand, 2),
            avg_daily_demand=round(avg_daily, 2),
            peak_date=peak['forecast_date'],
            peak_quantity=peak['predicted_quantity'],
        )

    
    def _save_forecasts(self, product_id: int, predictions: List[Dict]):
        """Save forecast predictions to database"""
        # Delete old forecasts for this product
        self.db.query(Forecast).filter(
            Forecast.product_id == product_id,
            Forecast.user_id == self.user_id
        ).delete()
        
        # Save new forecasts
        for p in predictions:
            forecast = Forecast(
                user_id=self.user_id,
                product_id=product_id,
                forecast_date=p['forecast_date'],
                predicted_quantity=p['predicted_quantity'],
                confidence_lower=p['confidence_lower'],
                confidence_upper=p['confidence_upper'],
                model_name=self.model_name
            )
            self.db.add(forecast)
        
        self.db.commit()
