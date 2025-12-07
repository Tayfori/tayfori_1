"""
Dashboard ve istatistik route'ları
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.database import get_db
from app.models.disaster import Disaster, DisasterStatus, DisasterSeverity
from app.models.victim import Victim, VictimStatus
from app.models.inventory import InventoryItem, ItemStatus
from app.models.user import User
from app.utils.security import get_current_user

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Dashboard istatistiklerini al"""

    # Afet istatistikleri
    total_disasters = db.query(Disaster).count()
    active_disasters = (
        db.query(Disaster).filter(Disaster.status == DisasterStatus.ACTIVE).count()
    )
    critical_disasters = (
        db.query(Disaster)
        .filter(Disaster.severity == DisasterSeverity.CRITICAL)
        .filter(Disaster.status == DisasterStatus.ACTIVE)
        .count()
    )

    # Afetzede istatistikleri
    total_victims = db.query(Victim).count()
    rescued_victims = (
        db.query(Victim).filter(Victim.status == VictimStatus.RESCUED).count()
    )
    missing_victims = (
        db.query(Victim).filter(Victim.status == VictimStatus.MISSING).count()
    )
    hospitalized_victims = (
        db.query(Victim).filter(Victim.status == VictimStatus.HOSPITALIZED).count()
    )

    # Envanter istatistikleri
    total_items = db.query(InventoryItem).count()
    low_stock_items = (
        db.query(InventoryItem)
        .filter(InventoryItem.quantity <= InventoryItem.min_quantity)
        .count()
    )
    depleted_items = (
        db.query(InventoryItem).filter(InventoryItem.status == ItemStatus.DEPLETED).count()
    )

    # Son afetler
    recent_disasters = (
        db.query(Disaster).order_by(Disaster.occurred_at.desc()).limit(5).all()
    )

    return {
        "disasters": {
            "total": total_disasters,
            "active": active_disasters,
            "critical": critical_disasters,
        },
        "victims": {
            "total": total_victims,
            "rescued": rescued_victims,
            "missing": missing_victims,
            "hospitalized": hospitalized_victims,
        },
        "inventory": {
            "total_items": total_items,
            "low_stock": low_stock_items,
            "depleted": depleted_items,
        },
        "recent_disasters": [
            {
                "id": d.id,
                "title": d.title,
                "type": d.disaster_type,
                "severity": d.severity,
                "status": d.status,
                "location": f"{d.city}, {d.location_name}",
                "occurred_at": d.occurred_at,
            }
            for d in recent_disasters
        ],
    }


@router.get("/map-data")
async def get_map_data(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Harita için afet verilerini al"""
    disasters = (
        db.query(Disaster)
        .filter(Disaster.latitude.isnot(None))
        .filter(Disaster.longitude.isnot(None))
        .filter(Disaster.status != DisasterStatus.ARCHIVED)
        .all()
    )

    return [
        {
            "id": d.id,
            "title": d.title,
            "type": d.disaster_type.value,
            "severity": d.severity.value,
            "status": d.status.value,
            "latitude": d.latitude,
            "longitude": d.longitude,
            "location": d.location_name,
            "city": d.city,
            "affected_people": d.estimated_affected_people,
        }
        for d in disasters
    ]


@router.get("/disaster-types")
async def get_disaster_type_stats(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Afet türlerine göre istatistikler"""
    stats = (
        db.query(Disaster.disaster_type, func.count(Disaster.id))
        .group_by(Disaster.disaster_type)
        .all()
    )

    return [{"type": disaster_type.value, "count": count} for disaster_type, count in stats]


@router.get("/needs-analysis")
async def get_needs_analysis(
    disaster_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """İhtiyaç analizi"""
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
        "priority_distribution": {
            "urgent": sum(1 for v in victims if v.priority.value == "urgent"),
            "high": sum(1 for v in victims if v.priority.value == "high"),
            "medium": sum(1 for v in victims if v.priority.value == "medium"),
            "low": sum(1 for v in victims if v.priority.value == "low"),
        },
    }
