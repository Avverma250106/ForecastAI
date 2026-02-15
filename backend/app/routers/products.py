"""
Products router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", response_model=List[dict])
def get_products(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Product, Inventory).join(
        Inventory, Product.id == Inventory.product_id
    ).filter(Product.user_id == current_user.id)

    if category:
        query = query.filter(Product.category == category)

    results = query.offset(skip).limit(limit).all()

    products = []
    for product, inventory in results:
        products.append({
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "category": product.category,
            "supplier_id": product.supplier_id,
            "unit_cost": product.unit_cost,
            "selling_price": product.unit_price,
            "reorder_point": product.reorder_point,
            "current_stock": inventory.quantity_on_hand or 0
        })

    return products


@router.post("/", response_model=ProductResponse)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new product"""
    # Check for duplicate SKU
    existing = db.query(Product).filter(
        Product.user_id == current_user.id,
        Product.sku == product_data.sku
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Product with SKU {product_data.sku} already exists"
        )
    
    # Create product
    product = Product(
        user_id=current_user.id,
        **product_data.model_dump()
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    
    # Create inventory record
    inventory = Inventory(
        user_id=current_user.id,
        product_id=product.id,
        quantity_on_hand=0
    )
    db.add(inventory)
    db.commit()
    
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a product"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = product_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a product"""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}


@router.get("/categories/list", response_model=List[str])
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of unique categories"""
    categories = db.query(Product.category).filter(
        Product.user_id == current_user.id,
        Product.category.isnot(None)
    ).distinct().all()
    return [c[0] for c in categories if c[0]]
