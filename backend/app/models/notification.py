"""
Bildirim modeli
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.database import Base
import enum


class NotificationType(str, enum.Enum):
    """Bildirim türleri"""

    ALERT = "alert"  # Uyarı
    INFO = "info"  # Bilgi
    WARNING = "warning"  # İkaz
    EMERGENCY = "emergency"  # Acil durum
    UPDATE = "update"  # Güncelleme


class NotificationStatus(str, enum.Enum):
    """Bildirim durumu"""

    PENDING = "pending"  # Bekliyor
    SENT = "sent"  # Gönderildi
    DELIVERED = "delivered"  # Teslim edildi
    READ = "read"  # Okundu
    FAILED = "failed"  # Başarısız


class Notification(Base):
    """Bildirimler tablosu"""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    # Bildirim içeriği
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(Enum(NotificationType), default=NotificationType.INFO)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)

    # Alıcı bilgileri
    recipient_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    recipient_user = relationship("User", foreign_keys=[recipient_user_id])

    # Toplu bildirim için
    target_role = Column(String(50), nullable=True)  # Belirli role gönder
    is_broadcast = Column(Boolean, default=False)  # Herkese gönder

    # İlişkili afet
    disaster_id = Column(Integer, ForeignKey("disasters.id"), nullable=True)
    disaster = relationship("Disaster", backref="notifications")

    # Gönderen
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sender = relationship("User", foreign_keys=[sender_id])

    # Öncelik
    priority = Column(Integer, default=0)  # 0: Normal, 1: Yüksek, 2: Acil

    # Kanal bilgileri
    send_email = Column(Boolean, default=False)
    send_sms = Column(Boolean, default=False)
    send_push = Column(Boolean, default=True)

    # Zaman damgaları
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Notification {self.title} ({self.status})>"
