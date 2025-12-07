"""
Kullanıcı modeli
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from app.models.database import Base
import enum


class UserRole(str, enum.Enum):
    """Kullanıcı rolleri"""

    ADMIN = "admin"  # Sistem yöneticisi
    COORDINATOR = "coordinator"  # Afet koordinatörü
    FIELD_WORKER = "field_worker"  # Saha çalışanı
    OBSERVER = "observer"  # Gözlemci (sadece görüntüleme)


class User(Base):
    """Kullanıcı tablosu"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.OBSERVER, nullable=False)

    # İletişim bilgileri
    phone = Column(String(20), nullable=True)
    department = Column(String(100), nullable=True)

    # Durum
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Zaman damgaları
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
