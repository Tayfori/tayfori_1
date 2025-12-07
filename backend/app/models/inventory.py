"""
Envanter modeli
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.app.models.database import Base
import enum


class ItemCategory(str, enum.Enum):
    """Malzeme kategorileri"""

    FOOD = "food"  # Gıda
    WATER = "water"  # Su
    MEDICAL = "medical"  # Tıbbi malzeme
    CLOTHING = "clothing"  # Giyim
    SHELTER = "shelter"  # Barınma
    HYGIENE = "hygiene"  # Hijyen
    TOOL = "tool"  # Araç-gereç
    EQUIPMENT = "equipment"  # Ekipman
    OTHER = "other"  # Diğer


class ItemStatus(str, enum.Enum):
    """Malzeme durumu"""

    AVAILABLE = "available"  # Mevcut
    IN_USE = "in_use"  # Kullanımda
    RESERVED = "reserved"  # Rezerve
    DEPLETED = "depleted"  # Tükendi
    DAMAGED = "damaged"  # Hasarlı


class InventoryItem(Base):
    """Envanter kalemleri tablosu"""

    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)

    # Malzeme bilgileri
    name = Column(String(255), nullable=False)
    category = Column(Enum(ItemCategory), nullable=False)
    description = Column(Text, nullable=True)
    unit = Column(String(50), nullable=False)  # Adet, kg, litre, vb.

    # Miktar bilgileri
    quantity = Column(Float, default=0)
    min_quantity = Column(Float, default=0)  # Minimum stok seviyesi
    max_quantity = Column(Float, nullable=True)  # Maksimum kapasite

    # Durum
    status = Column(Enum(ItemStatus), default=ItemStatus.AVAILABLE)

    # Konum
    storage_location = Column(String(255), nullable=True)
    warehouse_name = Column(String(255), nullable=True)

    # Tedarik bilgileri
    supplier = Column(String(255), nullable=True)
    last_resupply_date = Column(DateTime(timezone=True), nullable=True)

    # İlişkili afet (opsiyonel)
    disaster_id = Column(Integer, ForeignKey("disasters.id"), nullable=True)
    disaster = relationship("Disaster", backref="inventory_items")

    # Notlar
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<InventoryItem {self.name} ({self.quantity} {self.unit})>"


class InventoryTransaction(Base):
    """Envanter hareketleri tablosu"""

    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True, index=True)

    # İlişkiler
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    item = relationship("InventoryItem", backref="transactions")

    # İşlem bilgileri
    transaction_type = Column(
        String(50), nullable=False
    )  # "in" (giriş) veya "out" (çıkış)
    quantity = Column(Float, nullable=False)
    reason = Column(Text, nullable=True)

    # Kim tarafından
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", foreign_keys=[user_id])

    # Kime/Nereden
    recipient_name = Column(String(255), nullable=True)
    destination = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Transaction {self.transaction_type} {self.quantity}>"
