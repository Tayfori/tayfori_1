"""
Gönüllü API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import jwt

from ..models.database import get_db
from ..models.volunteer import VolunteerStatus
from ..schemas.volunteer import (
    VolunteerRegister,
    VolunteerLogin,
    VolunteerResponse,
    VolunteerListResponse,
    VolunteerProfileUpdate,
    VolunteerAuthResponse,
    VolunteerSkillAdd,
    VolunteerStats,
    Skill,
    SkillCreate,
    SkillUpdate,
    AssemblyPoint,
    AssemblyPointCreate,
    AssemblyPointUpdate
)
from ..services.volunteer_service import VolunteerService

router = APIRouter(prefix="/api/volunteers", tags=["Volunteers"])

# JWT Secret (normalde .env'den okunmalı)
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 gün


def create_access_token(data: dict):
    """JWT token oluştur"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_volunteer(
    token: str = Depends(lambda: None),  # TODO: OAuth2 scheme ekle
    db: Session = Depends(get_db)
):
    """Mevcut gönüllüyü al (token'dan)"""
    # Bu basit bir implementasyon, gerçekte OAuth2PasswordBearer kullanılmalı
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token gerekli"
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        volunteer_id: int = payload.get("sub")
        if volunteer_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Geçersiz token"
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz token"
        )

    service = VolunteerService(db)
    volunteer = service.get_volunteer(volunteer_id)
    if volunteer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Gönüllü bulunamadı"
        )

    return volunteer


# === Authentication ===

@router.post("/register", response_model=VolunteerResponse, status_code=status.HTTP_201_CREATED)
def register_volunteer(
    data: VolunteerRegister,
    db: Session = Depends(get_db)
):
    """
    Yeni gönüllü kaydı (dışarıdan kayıt).

    Herkes bu endpoint'i kullanabilir, onay için yönetici beklenir.
    """
    service = VolunteerService(db)
    volunteer = service.register_volunteer(data)
    return volunteer


@router.post("/login", response_model=VolunteerAuthResponse)
def login_volunteer(
    data: VolunteerLogin,
    db: Session = Depends(get_db)
):
    """Gönüllü girişi"""
    service = VolunteerService(db)
    volunteer = service.authenticate_volunteer(data.email, data.password)

    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email veya şifre hatalı"
        )

    if not volunteer.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hesabınız henüz onaylanmamış. Lütfen yönetici onayını bekleyin."
        )

    # JWT token oluştur
    access_token = create_access_token(data={"sub": volunteer.id})

    return VolunteerAuthResponse(
        access_token=access_token,
        volunteer=volunteer
    )


# === Profile Management ===

@router.get("/me", response_model=VolunteerResponse)
def get_my_profile(
    current_volunteer = Depends(get_current_volunteer)
):
    """Kendi profilini görüntüle"""
    return current_volunteer


@router.put("/me", response_model=VolunteerResponse)
def update_my_profile(
    data: VolunteerProfileUpdate,
    current_volunteer = Depends(get_current_volunteer),
    db: Session = Depends(get_db)
):
    """Kendi profilini güncelle"""
    service = VolunteerService(db)
    return service.update_volunteer_profile(current_volunteer.id, data)


@router.post("/me/photo", response_model=dict)
def upload_profile_photo(
    file: UploadFile = File(...),
    current_volunteer = Depends(get_current_volunteer),
    db: Session = Depends(get_db)
):
    """Profil fotoğrafı yükle"""
    service = VolunteerService(db)
    photo_url = service.upload_profile_photo(current_volunteer.id, file)
    return {"photo_url": photo_url}


# === Skills Management ===

@router.post("/me/skills", response_model=VolunteerResponse)
def add_my_skill(
    skill_data: VolunteerSkillAdd,
    current_volunteer = Depends(get_current_volunteer),
    db: Session = Depends(get_db)
):
    """Kendine yetkinlik ekle"""
    service = VolunteerService(db)
    return service.add_volunteer_skill(current_volunteer.id, skill_data)


@router.delete("/me/skills/{skill_id}", response_model=VolunteerResponse)
def remove_my_skill(
    skill_id: int,
    current_volunteer = Depends(get_current_volunteer),
    db: Session = Depends(get_db)
):
    """Kendinden yetkinlik çıkar"""
    service = VolunteerService(db)
    return service.remove_volunteer_skill(current_volunteer.id, skill_id)


# === Admin - Volunteer Management ===

@router.get("/", response_model=List[VolunteerListResponse])
def list_volunteers(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    city: Optional[str] = None,
    is_approved: Optional[bool] = None,
    skill_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Gönüllü listesi (admin için).

    Filtreler:
    - status: Durum (active, inactive, on_duty, unavailable)
    - city: Şehir
    - is_approved: Onaylı mı?
    - skill_id: Belirli yetkinliğe sahip olanlar
    """
    service = VolunteerService(db)

    status_enum = None
    if status:
        try:
            status_enum = VolunteerStatus[status.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Geçersiz durum: {status}"
            )

    volunteers = service.list_volunteers(
        skip=skip,
        limit=limit,
        status=status_enum,
        city=city,
        is_approved=is_approved,
        skill_id=skill_id
    )

    return volunteers


@router.get("/stats", response_model=VolunteerStats)
def get_volunteer_stats(db: Session = Depends(get_db)):
    """Gönüllü istatistikleri"""
    service = VolunteerService(db)
    return service.get_volunteer_stats()


@router.get("/{volunteer_id}", response_model=VolunteerResponse)
def get_volunteer(
    volunteer_id: int,
    db: Session = Depends(get_db)
):
    """Gönüllü detayı"""
    service = VolunteerService(db)
    volunteer = service.get_volunteer(volunteer_id)

    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gönüllü bulunamadı"
        )

    return volunteer


@router.post("/{volunteer_id}/approve", response_model=VolunteerResponse)
def approve_volunteer(
    volunteer_id: int,
    approved: bool = True,
    db: Session = Depends(get_db)
):
    """Gönüllü onaylama (admin)"""
    service = VolunteerService(db)
    return service.approve_volunteer(volunteer_id, approved)


@router.post("/{volunteer_id}/status", response_model=VolunteerResponse)
def change_volunteer_status(
    volunteer_id: int,
    new_status: str,
    db: Session = Depends(get_db)
):
    """Gönüllü durumu değiştir (admin)"""
    try:
        status_enum = VolunteerStatus[new_status.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Geçersiz durum: {new_status}"
        )

    service = VolunteerService(db)
    return service.change_volunteer_status(volunteer_id, status_enum)


# === Skills CRUD (Admin) ===

@router.get("/skills/all", response_model=List[Skill])
def list_skills(db: Session = Depends(get_db)):
    """Tüm yetkinlikler"""
    from ..models.volunteer import Skill as SkillModel
    return db.query(SkillModel).all()


@router.post("/skills/", response_model=Skill, status_code=status.HTTP_201_CREATED)
def create_skill(
    data: SkillCreate,
    db: Session = Depends(get_db)
):
    """Yeni yetkinlik oluştur (admin)"""
    from ..models.volunteer import Skill as SkillModel

    # Aynı isimde var mı?
    existing = db.query(SkillModel).filter(SkillModel.name == data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu isimde bir yetkinlik zaten var"
        )

    skill = SkillModel(**data.dict())
    db.add(skill)
    db.commit()
    db.refresh(skill)

    return skill


# === Assembly Points CRUD ===

@router.get("/assembly-points/", response_model=List[AssemblyPoint])
def list_assembly_points(
    is_active: Optional[bool] = None,
    city: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Toplanma noktaları listesi"""
    from ..models.volunteer import AssemblyPoint as AssemblyPointModel

    query = db.query(AssemblyPointModel)

    if is_active is not None:
        query = query.filter(AssemblyPointModel.is_active == is_active)
    if city:
        query = query.filter(AssemblyPointModel.city == city)

    return query.all()


@router.post("/assembly-points/", response_model=AssemblyPoint, status_code=status.HTTP_201_CREATED)
def create_assembly_point(
    data: AssemblyPointCreate,
    db: Session = Depends(get_db)
):
    """Yeni toplanma noktası oluştur (admin)"""
    from ..models.volunteer import AssemblyPoint as AssemblyPointModel

    assembly_point = AssemblyPointModel(**data.dict())
    db.add(assembly_point)
    db.commit()
    db.refresh(assembly_point)

    return assembly_point
