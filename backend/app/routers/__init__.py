"""
Routers package initialization
"""
from app.routers.auth import router as auth_router
from app.routers.products import router as products_router
from app.routers.suppliers import router as suppliers_router
from app.routers.sales import router as sales_router
from app.routers.inventory import router as inventory_router
from app.routers.forecasts import router as forecasts_router
from app.routers.alerts import router as alerts_router
from app.routers.purchase_orders import router as purchase_orders_router
from app.routers.dashboard import router as dashboard_router

__all__ = [
    "auth_router",
    "products_router",
    "suppliers_router",
    "sales_router",
    "inventory_router",
    "forecasts_router",
    "alerts_router",
    "purchase_orders_router",
    "dashboard_router"
]
