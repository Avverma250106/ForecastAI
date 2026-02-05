"""
Alert Service - Stockout prediction and notifications
"""
from datetime import date, datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.alert import Alert
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.forecast import Forecast
from app.models.supplier import Supplier
from app.config import settings


class AlertService:
    """
    Generates alerts based on inventory levels and demand forecasts.
    """
    
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
    
    def generate_alerts(self) -> Dict:
        """Generate alerts for all products"""
        results = {
            "created": 0,
            "stockout_warnings": 0,
            "low_stock": 0,
            "overstock": 0
        }
        
        # Get all products with inventory
        products = self.db.query(Product, Inventory).join(
            Inventory, Product.id == Inventory.product_id
        ).filter(
            Product.user_id == self.user_id
        ).all()
        
        today = date.today()
        
        for product, inventory in products:
            # Get supplier lead time
            lead_time = 7  # Default
            if product.supplier_id:
                supplier = self.db.query(Supplier).filter(
                    Supplier.id == product.supplier_id
                ).first()
                if supplier:
                    lead_time = supplier.lead_time_days
            
            # Get forecasted demand for lead time period
            forecast_demand = self.db.query(func.sum(Forecast.predicted_quantity)).filter(
                Forecast.product_id == product.id,
                Forecast.forecast_date >= today,
                Forecast.forecast_date < today + timedelta(days=lead_time + settings.safety_stock_days)
            ).scalar() or 0
            
            # Calculate available stock
            available = inventory.quantity_on_hand - inventory.quantity_reserved
            
            # Calculate days of stock
            avg_daily_demand = self._get_avg_daily_demand(product.id)
            days_of_stock = available / avg_daily_demand if avg_daily_demand > 0 else 999
            
            # Clear old unresolved alerts for this product
            self.db.query(Alert).filter(
                Alert.product_id == product.id,
                Alert.user_id == self.user_id,
                Alert.is_resolved == False
            ).delete()
            
            # Check for stockout risk
            if available <= 0:
                # Already out of stock
                self._create_alert(
                    product_id=product.id,
                    alert_type="stockout_warning",
                    priority="critical",
                    title=f"OUT OF STOCK: {product.name}",
                    message=f"Product {product.sku} is currently out of stock. Immediate reorder required.",
                    recommended_action=f"Order immediately from supplier",
                    recommended_quantity=self._calculate_reorder_qty(product, inventory, forecast_demand, lead_time)
                )
                results["stockout_warnings"] += 1
                results["created"] += 1
                
            elif days_of_stock <= lead_time + settings.safety_stock_days:
                # Stockout warning - will run out before reorder arrives
                priority = "critical" if days_of_stock <= lead_time else "high"
                self._create_alert(
                    product_id=product.id,
                    alert_type="stockout_warning",
                    priority=priority,
                    title=f"Stockout Risk: {product.name}",
                    message=f"Only {round(days_of_stock, 1)} days of stock remaining. Lead time is {lead_time} days.",
                    recommended_action=f"Order within {max(0, round(days_of_stock - lead_time))} days",
                    recommended_quantity=self._calculate_reorder_qty(product, inventory, forecast_demand, lead_time)
                )
                results["stockout_warnings"] += 1
                results["created"] += 1
                
            elif available <= product.reorder_point:
                # Low stock - approaching reorder point
                self._create_alert(
                    product_id=product.id,
                    alert_type="low_stock",
                    priority="medium",
                    title=f"Low Stock: {product.name}",
                    message=f"Stock level ({available}) is at or below reorder point ({product.reorder_point}).",
                    recommended_action="Consider placing an order soon",
                    recommended_quantity=self._calculate_reorder_qty(product, inventory, forecast_demand, lead_time)
                )
                results["low_stock"] += 1
                results["created"] += 1
                
            elif available > product.reorder_point * 4:
                # Overstock warning
                self._create_alert(
                    product_id=product.id,
                    alert_type="overstock",
                    priority="low",
                    title=f"Overstock: {product.name}",
                    message=f"Stock level ({available}) is significantly above reorder point. Consider reducing future orders.",
                    recommended_action="Review ordering patterns"
                )
                results["overstock"] += 1
                results["created"] += 1
        
        self.db.commit()
        return results
    
    def _get_avg_daily_demand(self, product_id: int) -> float:
        """Get average daily demand from recent sales or forecasts"""
        from app.models.sale import Sale
        
        # Look at last 30 days of sales
        thirty_days_ago = date.today() - timedelta(days=30)
        
        total_qty = self.db.query(func.sum(Sale.quantity)).filter(
            Sale.product_id == product_id,
            Sale.user_id == self.user_id,
            Sale.sale_date >= thirty_days_ago
        ).scalar() or 0
        
        return total_qty / 30
    
    def _calculate_reorder_qty(
        self,
        product: Product,
        inventory: Inventory,
        forecast_demand: float,
        lead_time: int
    ) -> int:
        """Calculate recommended reorder quantity"""
        # Get minimum order quantity from supplier
        min_order = 1
        if product.supplier_id:
            supplier = self.db.query(Supplier).filter(
                Supplier.id == product.supplier_id
            ).first()
            if supplier:
                min_order = supplier.minimum_order_quantity
        
        # Calculate demand for lead time + safety period + buffer
        avg_daily = self._get_avg_daily_demand(product.id)
        target_days = lead_time + settings.safety_stock_days + 30  # Order for 30 days after safety stock
        target_stock = avg_daily * target_days
        
        # Calculate reorder quantity
        available = inventory.quantity_on_hand - inventory.quantity_reserved
        reorder_qty = max(0, target_stock - available - inventory.quantity_on_order)
        
        # Round up to minimum order quantity
        if reorder_qty > 0 and reorder_qty < min_order:
            reorder_qty = min_order
        
        return int(reorder_qty)
    
    def _create_alert(
        self,
        product_id: int,
        alert_type: str,
        priority: str,
        title: str,
        message: str,
        recommended_action: str = None,
        recommended_quantity: int = None
    ):
        """Create and save an alert"""
        alert = Alert(
            user_id=self.user_id,
            product_id=product_id,
            alert_type=alert_type,
            priority=priority,
            title=title,
            message=message,
            recommended_action=recommended_action,
            recommended_quantity=recommended_quantity,
            expires_at=datetime.utcnow() + timedelta(days=7)  # Alerts expire after 7 days
        )
        self.db.add(alert)
