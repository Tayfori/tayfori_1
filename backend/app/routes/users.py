"""
Kullanıcı yönetimi route'ları
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.app.models.database import get_db
from backend.app.models.user import User, UserRole
from backend.app.utils.security import get_current_user, require_admin

router = APIRouter()


class UserUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    department: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


@router.get("/")
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Kullanıcıları listele"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Kullanıcı detaylarını al"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    return user


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Kullanıcı bilgilerini güncelle (Admin)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    if user_data.full_name:
        user.full_name = user_data.full_name
    if user_data.phone:
        user.phone = user_data.phone
    if user_data.department:
        user.department = user_data.department
    if user_data.role:
        user.role = user_data.role
    if user_data.is_active is not None:
        user.is_active = user_data.is_active

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Kullanıcıyı sil (Admin)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    db.delete(user)
    db.commit()
    return {"message": "Kullanıcı silindi"}
