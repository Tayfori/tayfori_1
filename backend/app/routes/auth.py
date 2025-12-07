"""
Kimlik doğrulama route'ları
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from backend.app.models.database import get_db
from backend.app.models.user import User, UserRole
from backend.app.utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
)
from backend.config import settings

router = APIRouter()


# Pydantic modeller
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str
    phone: str | None = None
    department: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Yeni kullanıcı kaydı"""

    # Email kontrolü
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email adresi zaten kayıtlı",
        )

    # Username kontrolü
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kullanıcı adı zaten alınmış",
        )

    # Yeni kullanıcı oluştur
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        phone=user_data.phone,
        department=user_data.department,
        role=UserRole.OBSERVER,  # Varsayılan rol
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """Kullanıcı girişi"""

    # Kullanıcıyı bul (email veya username ile)
    user = (
        db.query(User)
        .filter(
            (User.email == form_data.username) | (User.username == form_data.username)
        )
        .first()
    )

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email/kullanıcı adı veya şifre hatalı",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Kullanıcı hesabı pasif"
        )

    # Last login güncelle
    user.last_login = datetime.utcnow()
    db.commit()

    # Token oluştur
    access_token = create_access_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
        },
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Mevcut kullanıcı bilgilerini al"""
    return current_user


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Şifre değiştir"""

    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Mevcut şifre hatalı"
        )

    current_user.hashed_password = get_password_hash(new_password)
    db.commit()

    return {"message": "Şifre başarıyla değiştirildi"}
