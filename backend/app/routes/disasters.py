"""
Afet yönetimi route'ları
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.app.models.database import get_db
from backend.app.models.disaster import Disaster, DisasterType, DisasterSeverity, DisasterStatus
from backend.app.models.user import User
from backend.app.utils.security import get_current_user, require_coordinator_or_admin

router = APIRouter()


class DisasterCreate(BaseModel):
    title: str
    description: str | None = None
    disaster_type: DisasterType
    severity: DisasterSeverity
    location_name: str
    city: str
    district: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    occurred_at: datetime
    estimated_affected_people: int = 0


class DisasterUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    severity: DisasterSeverity | None = None
    status: DisasterStatus | None = None
    confirmed_deaths: int | None = None
    confirmed_injured: int | None = None
    missing_people: int | None = None
    estimated_affected_people: int | None = None


@router.get("/")
async def list_disasters(
    skip: int = 0,
    limit: int = 100,
    status: DisasterStatus | None = None,
    disaster_type: DisasterType | None = None,
    city: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Afetleri listele"""
    query = db.query(Disaster)

    if status:
        query = query.filter(Disaster.status == status)
    if disaster_type:
        query = query.filter(Disaster.disaster_type == disaster_type)
    if city:
        query = query.filter(Disaster.city.ilike(f"%{city}%"))

    disasters = query.order_by(Disaster.occurred_at.desc()).offset(skip).limit(limit).all()
    return disasters


@router.get("/{disaster_id}")
async def get_disaster(
    disaster_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Afet detaylarını al"""
    disaster = db.query(Disaster).filter(Disaster.id == disaster_id).first()
    if not disaster:
        raise HTTPException(status_code=404, detail="Afet kaydı bulunamadı")
    return disaster


@router.post("/", status_code=201)
async def create_disaster(
    disaster_data: DisasterCreate,
    current_user: User = Depends(require_coordinator_or_admin),
    db: Session = Depends(get_db),
):
    """Yeni afet kaydı oluştur"""
    new_disaster = Disaster(
        **disaster_data.model_dump(),
        reported_by_id=current_user.id,
        status=DisasterStatus.ACTIVE,
    )

    db.add(new_disaster)
    db.commit()
    db.refresh(new_disaster)
    return new_disaster


@router.put("/{disaster_id}")
async def update_disaster(
    disaster_id: int,
    disaster_data: DisasterUpdate,
    current_user: User = Depends(require_coordinator_or_admin),
    db: Session = Depends(get_db),
):
    """Afet kaydını güncelle"""
    disaster = db.query(Disaster).filter(Disaster.id == disaster_id).first()
    if not disaster:
        raise HTTPException(status_code=404, detail="Afet kaydı bulunamadı")

    update_data = disaster_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(disaster, field, value)

    # Eğer status resolved olarak değiştiriliyorsa, resolved_at'i ayarla
    if disaster_data.status == DisasterStatus.RESOLVED and not disaster.resolved_at:
        disaster.resolved_at = datetime.utcnow()

    db.commit()
    db.refresh(disaster)
    return disaster


@router.delete("/{disaster_id}")
async def delete_disaster(
    disaster_id: int,
    current_user: User = Depends(require_coordinator_or_admin),
    db: Session = Depends(get_db),
):
    """Afet kaydını sil"""
    disaster = db.query(Disaster).filter(Disaster.id == disaster_id).first()
    if not disaster:
        raise HTTPException(status_code=404, detail="Afet kaydı bulunamadı")

    db.delete(disaster)
    db.commit()
    return {"message": "Afet kaydı silindi"}


@router.get("/{disaster_id}/stats")
async def get_disaster_stats(
    disaster_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Afet istatistiklerini al"""
    disaster = db.query(Disaster).filter(Disaster.id == disaster_id).first()
    if not disaster:
        raise HTTPException(status_code=404, detail="Afet kaydı bulunamadı")

    # İstatistikleri hesapla
    victim_count = len(disaster.victims)
    inventory_items = len(disaster.inventory_items)

    return {
        "disaster": disaster,
        "stats": {
            "victim_count": victim_count,
            "inventory_items": inventory_items,
            "confirmed_deaths": disaster.confirmed_deaths,
            "confirmed_injured": disaster.confirmed_injured,
            "missing_people": disaster.missing_people,
            "estimated_affected": disaster.estimated_affected_people,
        },
    }
