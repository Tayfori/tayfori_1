"""
Afetzede yönetimi route'ları
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.app.models.database import get_db
from backend.app.models.victim import Victim, VictimStatus, VictimPriority
from backend.app.models.user import User
from backend.app.utils.security import get_current_user, require_coordinator_or_admin

router = APIRouter()


class VictimCreate(BaseModel):
    disaster_id: int
    tc_no: str | None = None
    full_name: str
    age: int | None = None
    gender: str | None = None
    phone: str | None = None
    emergency_contact: str | None = None
    emergency_contact_name: str | None = None
    health_condition: str | None = None
    special_needs: str | None = None
    current_location: str | None = None
    family_members_count: int = 0
    needs_food: bool = False
    needs_water: bool = False
    needs_shelter: bool = False
    needs_medical: bool = False
    needs_clothing: bool = False
    notes: str | None = None


class VictimUpdate(BaseModel):
    status: VictimStatus | None = None
    priority: VictimPriority | None = None
    health_condition: str | None = None
    current_location: str | None = None
    shelter_name: str | None = None
    needs_food: bool | None = None
    needs_water: bool | None = None
    needs_shelter: bool | None = None
    needs_medical: bool | None = None
    needs_clothing: bool | None = None
    notes: str | None = None


@router.get("/")
async def list_victims(
    skip: int = 0,
    limit: int = 100,
    disaster_id: int | None = None,
    status: VictimStatus | None = None,
    priority: VictimPriority | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Afetzedeleri listele"""
    query = db.query(Victim)

    if disaster_id:
        query = query.filter(Victim.disaster_id == disaster_id)
    if status:
        query = query.filter(Victim.status == status)
    if priority:
        query = query.filter(Victim.priority == priority)

    victims = query.offset(skip).limit(limit).all()
    return victims


@router.get("/{victim_id}")
async def get_victim(
    victim_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Afetzede detaylarını al"""
    victim = db.query(Victim).filter(Victim.id == victim_id).first()
    if not victim:
        raise HTTPException(status_code=404, detail="Afetzede kaydı bulunamadı")
    return victim


@router.post("/", status_code=201)
async def create_victim(
    victim_data: VictimCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Yeni afetzede kaydı oluştur"""
    new_victim = Victim(**victim_data.model_dump(), registered_by_id=current_user.id)

    db.add(new_victim)
    db.commit()
    db.refresh(new_victim)
    return new_victim


@router.put("/{victim_id}")
async def update_victim(
    victim_id: int,
    victim_data: VictimUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Afetzede kaydını güncelle"""
    victim = db.query(Victim).filter(Victim.id == victim_id).first()
    if not victim:
        raise HTTPException(status_code=404, detail="Afetzede kaydı bulunamadı")

    update_data = victim_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(victim, field, value)

    db.commit()
    db.refresh(victim)
    return victim


@router.delete("/{victim_id}")
async def delete_victim(
    victim_id: int,
    current_user: User = Depends(require_coordinator_or_admin),
    db: Session = Depends(get_db),
):
    """Afetzede kaydını sil"""
    victim = db.query(Victim).filter(Victim.id == victim_id).first()
    if not victim:
        raise HTTPException(status_code=404, detail="Afetzede kaydı bulunamadı")

    db.delete(victim)
    db.commit()
    return {"message": "Afetzede kaydı silindi"}


@router.get("/needs/summary")
async def get_needs_summary(
    disaster_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """İhtiyaç özeti"""
    query = db.query(Victim)
    if disaster_id:
        query = query.filter(Victim.disaster_id == disaster_id)

    victims = query.all()

    return {
        "total_victims": len(victims),
        "needs": {
            "food": sum(1 for v in victims if v.needs_food),
            "water": sum(1 for v in victims if v.needs_water),
            "shelter": sum(1 for v in victims if v.needs_shelter),
            "medical": sum(1 for v in victims if v.needs_medical),
            "clothing": sum(1 for v in victims if v.needs_clothing),
        },
    }
