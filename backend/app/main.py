"""
AI Demand Forecasting Platform - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import (
    auth_router,
    products_router,
    suppliers_router,
    sales_router,
    inventory_router,
    forecasts_router,
    alerts_router,
    purchase_orders_router,
    dashboard_router
)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-powered demand forecasting platform for retailers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(dashboard_router, prefix=settings.api_prefix)
app.include_router(products_router, prefix=settings.api_prefix)
app.include_router(suppliers_router, prefix=settings.api_prefix)
app.include_router(sales_router, prefix=settings.api_prefix)
app.include_router(inventory_router, prefix=settings.api_prefix)
app.include_router(forecasts_router, prefix=settings.api_prefix)
app.include_router(alerts_router, prefix=settings.api_prefix)
app.include_router(purchase_orders_router, prefix=settings.api_prefix)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check for monitoring"""
    return {"status": "healthy"}
