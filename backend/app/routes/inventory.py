"""
Envanter yönetimi route'ları
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.database import get_db
from app.models.inventory import (
    InventoryItem,
    InventoryTransaction,
    ItemCategory,
    ItemStatus,
)
from app.models.user import User
from app.utils.security import get_current_user, require_coordinator_or_admin

router = APIRouter()


class ItemCreate(BaseModel):
    name: str
    category: ItemCategory
    description: str | None = None
    unit: str
    quantity: float
    min_quantity: float = 0
    storage_location: str | None = None
    warehouse_name: str | None = None
    disaster_id: int | None = None


class ItemUpdate(BaseModel):
    name: str | None = None
    quantity: float | None = None
    min_quantity: float | None = None
    status: ItemStatus | None = None
    storage_location: str | None = None
    notes: str | None = None


class TransactionCreate(BaseModel):
    item_id: int
    transaction_type: str  # "in" veya "out"
    quantity: float
    reason: str | None = None
    recipient_name: str | None = None
    destination: str | None = None


@router.get("/items")
async def list_items(
    skip: int = 0,
    limit: int = 100,
    category: ItemCategory | None = None,
    status: ItemStatus | None = None,
    disaster_id: int | None = None,
    low_stock: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Envanter kalemlerini listele"""
    query = db.query(InventoryItem)

    if category:
        query = query.filter(InventoryItem.category == category)
    if status:
        query = query.filter(InventoryItem.status == status)
    if disaster_id:
        query = query.filter(InventoryItem.disaster_id == disaster_id)
    if low_stock:
        query = query.filter(InventoryItem.quantity <= InventoryItem.min_quantity)

    items = query.offset(skip).limit(limit).all()
    return items


@router.get("/items/{item_id}")
async def get_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Envanter kalemi detaylarını al"""
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Envanter kalemi bulunamadı")
    return item


@router.post("/items", status_code=201)
async def create_item(
    item_data: ItemCreate,
    current_user: User = Depends(require_coordinator_or_admin),
    db: Session = Depends(get_db),
):
    """Yeni envanter kalemi oluştur"""
    new_item = InventoryItem(**item_data.model_dump())

    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item_data: ItemUpdate,
    current_user: User = Depends(require_coordinator_or_admin),
    db: Session = Depends(get_db),
):
    """Envanter kalemini güncelle"""
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Envanter kalemi bulunamadı")

    update_data = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/items/{item_id}")
async def delete_item(
    item_id: int,
    current_user: User = Depends(require_coordinator_or_admin),
    db: Session = Depends(get_db),
):
    """Envanter kalemini sil"""
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Envanter kalemi bulunamadı")

    db.delete(item)
    db.commit()
    return {"message": "Envanter kalemi silindi"}


@router.post("/transactions", status_code=201)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Envanter hareketi oluştur (giriş/çıkış)"""
    item = (
        db.query(InventoryItem)
        .filter(InventoryItem.id == transaction_data.item_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Envanter kalemi bulunamadı")

    # Stok güncelle
    if transaction_data.transaction_type == "in":
        item.quantity += transaction_data.quantity
    elif transaction_data.transaction_type == "out":
        if item.quantity < transaction_data.quantity:
            raise HTTPException(
                status_code=400, detail="Yetersiz stok miktarı"
            )
        item.quantity -= transaction_data.quantity
    else:
        raise HTTPException(
            status_code=400,
            detail="Geçersiz işlem tipi (in veya out olmalı)",
        )

    # Transaction oluştur
    new_transaction = InventoryTransaction(
        **transaction_data.model_dump(), user_id=current_user.id
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction


@router.get("/transactions")
async def list_transactions(
    skip: int = 0,
    limit: int = 100,
    item_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Envanter hareketlerini listele"""
    query = db.query(InventoryTransaction)

    if item_id:
        query = query.filter(InventoryTransaction.item_id == item_id)

    transactions = (
        query.order_by(InventoryTransaction.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return transactions


@router.get("/summary")
async def get_inventory_summary(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Envanter özeti"""
    items = db.query(InventoryItem).all()

    summary = {
        "total_items": len(items),
        "by_category": {},
        "low_stock_items": [],
        "depleted_items": [],
    }

    for category in ItemCategory:
        category_items = [i for i in items if i.category == category]
        summary["by_category"][category.value] = len(category_items)

    summary["low_stock_items"] = [
        {"id": i.id, "name": i.name, "quantity": i.quantity, "min_quantity": i.min_quantity}
        for i in items
        if i.quantity <= i.min_quantity
    ]

    summary["depleted_items"] = [
        {"id": i.id, "name": i.name}
        for i in items
        if i.status == ItemStatus.DEPLETED
    ]

    return summary
