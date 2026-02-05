"""
Suppliers router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.supplier import Supplier
from app.models.user import User
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.get("/", response_model=List[SupplierResponse])
def get_suppliers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all suppliers for current user"""
    return db.query(Supplier).filter(Supplier.user_id == current_user.id).all()


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific supplier"""
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id,
        Supplier.user_id == current_user.id
    ).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.post("/", response_model=SupplierResponse)
def create_supplier(
    supplier_data: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new supplier"""
    supplier = Supplier(
        user_id=current_user.id,
        **supplier_data.model_dump()
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    supplier_data: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a supplier"""
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id,
        Supplier.user_id == current_user.id
    ).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    update_data = supplier_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(supplier, key, value)
    
    db.commit()
    db.refresh(supplier)
    return supplier


@router.delete("/{supplier_id}")
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a supplier"""
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id,
        Supplier.user_id == current_user.id
    ).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    db.delete(supplier)
    db.commit()
    return {"message": "Supplier deleted successfully"}
