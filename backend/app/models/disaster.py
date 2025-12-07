"""
Afet modeli
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.app.models.database import Base
import enum


class DisasterType(str, enum.Enum):
    """Afet türleri"""

    EARTHQUAKE = "earthquake"  # Deprem
    FLOOD = "flood"  # Sel
    FIRE = "fire"  # Yangın
    LANDSLIDE = "landslide"  # Heyelan
    AVALANCHE = "avalanche"  # Çığ
    STORM = "storm"  # Fırtına
    DROUGHT = "drought"  # Kuraklık
    EPIDEMIC = "epidemic"  # Salgın
    OTHER = "other"  # Diğer


class DisasterSeverity(str, enum.Enum):
    """Afet şiddeti"""

    LOW = "low"  # Düşük
    MEDIUM = "medium"  # Orta
    HIGH = "high"  # Yüksek
    CRITICAL = "critical"  # Kritik


class DisasterStatus(str, enum.Enum):
    """Afet durumu"""

    ACTIVE = "active"  # Aktif
    MONITORING = "monitoring"  # İzleniyor
    RESOLVED = "resolved"  # Çözüldü
    ARCHIVED = "archived"  # Arşivlendi


class Disaster(Base):
    """Afet kayıtları tablosu"""

    __tablename__ = "disasters"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    disaster_type = Column(Enum(DisasterType), nullable=False)
    severity = Column(Enum(DisasterSeverity), default=DisasterSeverity.MEDIUM)
    status = Column(Enum(DisasterStatus), default=DisasterStatus.ACTIVE)

    # Konum bilgileri
    location_name = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    district = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    affected_area_km2 = Column(Float, nullable=True)

    # İstatistikler
    estimated_affected_people = Column(Integer, default=0)
    confirmed_deaths = Column(Integer, default=0)
    confirmed_injured = Column(Integer, default=0)
    missing_people = Column(Integer, default=0)

    # Zaman bilgileri
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    reported_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # İlişkiler
    reported_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reported_by = relationship("User", foreign_keys=[reported_by_id])

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Disaster {self.title} ({self.disaster_type})>"
