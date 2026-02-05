"""
AI Demand Forecasting Platform - Configuration
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    app_name: str = "AI Demand Forecasting"
    debug: bool = True
    api_prefix: str = "/api/v1"
    
    # Database (PostgreSQL)
    database_url: str = "postgresql://postgres:password@localhost:5432/demand_forecast"
    
    # JWT Authentication
    secret_key: str = "your-secret-key-change-in-production-12345"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    
    # ML Model Settings
    ml_model_path: str = "./models"
    forecast_horizon_days: int = 90
    safety_stock_days: int = 7
    
    # Alert Settings
    stockout_warning_days: int = 14
    
    model_config = {
        "env_file": ".env",
        "protected_namespaces": ("settings_",)
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
