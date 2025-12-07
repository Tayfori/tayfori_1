"""
Afet Çağrısı API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..models.database import get_db
from ..models.user import User  # Yönetici için
from ..schemas.disaster_call import (
    DisasterCallCreate,
    DisasterCallUpdate,
    DisasterCallResponse,
    VolunteerMatchingRequest,
    VolunteerMatchingResponse,
    VolunteerAssignmentResponse,
    VolunteerAssignmentUpdate,
    DisasterCallStatusEnum,
    VolunteerAssignmentStatusEnum
)
from ..services.disaster_call_service import DisasterCallService

router = APIRouter(prefix="/api/disaster-calls", tags=["Disaster Calls"])


# === CRUD Operations ===

@router.post("/", response_model=DisasterCallResponse, status_code=status.HTTP_201_CREATED)
def create_disaster_call(
    data: DisasterCallCreate,
    db: Session = Depends(get_db)
    # TODO: current_user: User = Depends(get_current_user)
):
    """
    Yeni afet çağrısı oluştur (yönetici).

    Bir afet için gönüllü çağrısı oluşturur.
    """
    service = DisasterCallService(db)
    # created_by = current_user.id
    created_by = 1  # TODO: Gerçek user ID kullan

    disaster_call = service.create_disaster_call(data, created_by)
    return disaster_call


@router.get("/", response_model=List[DisasterCallResponse])
def list_disaster_calls(
    disaster_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Afet çağrıları listesi.

    Filtreler:
    - disaster_id: Belirli bir afet için
    - status: Durum (draft, active, in_progress, completed, cancelled)
    """
    service = DisasterCallService(db)

    status_enum = None
    if status:
        try:
            status_enum = DisasterCallStatusEnum[status.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Geçersiz durum: {status}"
            )

    calls = service.list_disaster_calls(
        disaster_id=disaster_id,
        status=status_enum,
        skip=skip,
        limit=limit
    )

    return calls


@router.get("/{call_id}", response_model=DisasterCallResponse)
def get_disaster_call(
    call_id: int,
    db: Session = Depends(get_db)
):
    """Afet çağrısı detayı"""
    service = DisasterCallService(db)
    disaster_call = service.get_disaster_call(call_id)

    if not disaster_call:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Afet çağrısı bulunamadı"
        )

    return disaster_call


@router.put("/{call_id}", response_model=DisasterCallResponse)
def update_disaster_call(
    call_id: int,
    data: DisasterCallUpdate,
    db: Session = Depends(get_db)
):
    """Afet çağrısı güncelle"""
    service = DisasterCallService(db)
    return service.update_disaster_call(call_id, data)


@router.post("/{call_id}/activate", response_model=DisasterCallResponse)
def activate_disaster_call(
    call_id: int,
    db: Session = Depends(get_db)
):
    """
    Afet çağrısını aktif et.

    Çağrı aktif olduğunda gönüllüler bildirim almaya başlar.
    """
    service = DisasterCallService(db)
    return service.activate_disaster_call(call_id)


# === Volunteer Matching & Assignment ===

@router.post("/match", response_model=VolunteerMatchingResponse)
def match_volunteers(
    request: VolunteerMatchingRequest,
    db: Session = Depends(get_db)
):
    """
    Afet çağrısı için en uygun gönüllüleri bul.

    Akıllı eşleştirme algoritması kullanılır:
    - Yetkinlik eşleşmesi (%40)
    - Mesafe (%30)
    - Rating (%20)
    - Deneyim (%10)

    Parametreler:
    - max_distance_km: Maksimum mesafe (km)
    - auto_assign: Otomatik atama yap
    - auto_notify: Otomatik bildirim gönder
    """
    service = DisasterCallService(db)
    return service.match_volunteers(request)


@router.post("/{call_id}/assign/{volunteer_id}", response_model=VolunteerAssignmentResponse)
def assign_volunteer(
    call_id: int,
    volunteer_id: int,
    db: Session = Depends(get_db)
):
    """
    Manuel gönüllü atama.

    Yönetici belirli bir gönüllüyü afet çağrısına atar.
    """
    service = DisasterCallService(db)
    assignment = service.assign_volunteer(
        disaster_call_id=call_id,
        volunteer_id=volunteer_id,
        auto_notify=True
    )
    return assignment


@router.get("/{call_id}/assignments", response_model=List[VolunteerAssignmentResponse])
def get_call_assignments(
    call_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Afet çağrısına atanan gönüllüler.

    Filtre:
    - status: Atama durumu (pending, accepted, rejected, arrived, completed, cancelled)
    """
    service = DisasterCallService(db)

    status_enum = None
    if status:
        try:
            status_enum = VolunteerAssignmentStatusEnum[status.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Geçersiz durum: {status}"
            )

    assignments = service.get_call_assignments(call_id, status_enum)
    return assignments


# === Volunteer Actions ===

@router.post("/assignments/{assignment_id}/respond")
def respond_to_assignment(
    assignment_id: int,
    accept: bool,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
    # TODO: current_volunteer = Depends(get_current_volunteer)
):
    """
    Gönüllü atamaya cevap verir (kabul/red).

    Gönüllüler bu endpoint ile çağrıyı kabul veya reddedebilir.
    """
    service = DisasterCallService(db)
    volunteer_id = 1  # TODO: Gerçek volunteer ID kullan

    assignment = service.respond_to_assignment(
        assignment_id=assignment_id,
        volunteer_id=volunteer_id,
        accept=accept,
        notes=notes
    )

    return {"message": "Yanıt kaydedildi", "assignment": assignment}


@router.get("/assignments/my", response_model=List[VolunteerAssignmentResponse])
def get_my_assignments(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
    # TODO: current_volunteer = Depends(get_current_volunteer)
):
    """
    Kendi atamalarımı görüntüle.

    Gönüllülerin kendi çağrılarını görmesi için.
    """
    service = DisasterCallService(db)
    volunteer_id = 1  # TODO: Gerçek volunteer ID kullan

    status_enum = None
    if status:
        try:
            status_enum = VolunteerAssignmentStatusEnum[status.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Geçersiz durum: {status}"
            )

    assignments = service.get_volunteer_assignments(volunteer_id, status_enum)
    return assignments


# === Notifications ===

@router.post("/{call_id}/notify")
def send_broadcast_notification(
    call_id: int,
    title: str,
    message: str,
    db: Session = Depends(get_db)
):
    """
    Tüm atanan gönüllülere toplu bildirim gönder.

    Yöneticiler afet çağrısındaki tüm gönüllülere bildirim gönderebilir.
    """
    service = DisasterCallService(db)
    service.send_broadcast_notification(call_id, title, message)

    return {"message": "Bildirim gönderildi"}
