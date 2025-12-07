"""
Afetzede modeli
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.database import Base
import enum


class VictimStatus(str, enum.Enum):
    """Afetzede durumu"""

    RESCUED = "rescued"  # Kurtarıldı
    IN_SHELTER = "in_shelter"  # Barınakta
    HOSPITALIZED = "hospitalized"  # Hastanede
    MISSING = "missing"  # Kayıp
    DECEASED = "deceased"  # Vefat
    RELOCATED = "relocated"  # Yerleştirildi


class VictimPriority(str, enum.Enum):
    """Öncelik durumu"""

    LOW = "low"  # Düşük
    MEDIUM = "medium"  # Orta
    HIGH = "high"  # Yüksek
    URGENT = "urgent"  # Acil


class Victim(Base):
    """Afetzede kayıtları tablosu"""

    __tablename__ = "victims"

    id = Column(Integer, primary_key=True, index=True)

    # Kişisel bilgiler
    tc_no = Column(String(11), unique=True, index=True, nullable=True)
    full_name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)

    # İletişim
    phone = Column(String(20), nullable=True)
    emergency_contact = Column(String(20), nullable=True)
    emergency_contact_name = Column(String(255), nullable=True)

    # Durum
    status = Column(Enum(VictimStatus), default=VictimStatus.RESCUED)
    priority = Column(Enum(VictimPriority), default=VictimPriority.MEDIUM)
    health_condition = Column(Text, nullable=True)
    special_needs = Column(Text, nullable=True)  # Özel ihtiyaçlar (bebek, yaşlı, engelli)

    # Konum bilgileri
    current_location = Column(String(255), nullable=True)
    shelter_name = Column(String(255), nullable=True)

    # Aile bilgileri
    family_members_count = Column(Integer, default=0)
    family_members_info = Column(Text, nullable=True)

    # İhtiyaçlar
    needs_food = Column(Boolean, default=False)
    needs_water = Column(Boolean, default=False)
    needs_shelter = Column(Boolean, default=False)
    needs_medical = Column(Boolean, default=False)
    needs_clothing = Column(Boolean, default=False)
    other_needs = Column(Text, nullable=True)

    # İlişkiler
    disaster_id = Column(Integer, ForeignKey("disasters.id"), nullable=False)
    disaster = relationship("Disaster", backref="victims")

    registered_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    registered_by = relationship("User", foreign_keys=[registered_by_id])

    # Notlar
    notes = Column(Text, nullable=True)

    # Zaman damgaları
    rescue_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Victim {self.full_name} ({self.status})>"
