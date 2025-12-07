"""
Gönüllü servisi
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status, UploadFile
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import os
import uuid

from ..models.volunteer import Volunteer, Skill, AssemblyPoint, VolunteerStatus, volunteer_skills
from ..models.disaster_call import (
    DisasterCall,
    VolunteerAssignment,
    DisasterCallSkill,
    VolunteerAssignmentStatus,
    Notification
)
from ..schemas.volunteer import (
    VolunteerRegister,
    VolunteerProfileUpdate,
    VolunteerSkillAdd,
    VolunteerStats
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class VolunteerService:
    """Gönüllü yönetim servisi"""

    def __init__(self, db: Session):
        self.db = db

    # === Authentication ===

    def register_volunteer(self, data: VolunteerRegister) -> Volunteer:
        """Yeni gönüllü kaydı"""
        # Email kontrolü
        existing = self.db.query(Volunteer).filter(
            or_(
                Volunteer.email == data.email,
                Volunteer.tc_no == data.tc_no
            )
        ).first()

        if existing:
            if existing.email == data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Bu email adresi zaten kullanılıyor"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Bu TC kimlik numarası zaten kayıtlı"
                )

        # Şifre hash
        hashed_password = pwd_context.hash(data.password)

        # Gönüllü oluştur
        volunteer = Volunteer(
            tc_no=data.tc_no,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            phone=data.phone,
            password_hash=hashed_password,
            city=data.city,
            district=data.district,
            address=data.address,
            birth_date=data.birth_date,
            gender=data.gender,
            status=VolunteerStatus.ACTIVE,
            is_verified=False,  # Email doğrulaması gerekiyor
            is_approved=False,  # Yönetici onayı gerekiyor
        )

        self.db.add(volunteer)
        self.db.commit()
        self.db.refresh(volunteer)

        return volunteer

    def authenticate_volunteer(self, email: str, password: str) -> Optional[Volunteer]:
        """Gönüllü girişi"""
        volunteer = self.db.query(Volunteer).filter(
            Volunteer.email == email
        ).first()

        if not volunteer:
            return None

        if not pwd_context.verify(password, volunteer.password_hash):
            return None

        # Son giriş zamanını güncelle
        volunteer.last_login = datetime.utcnow()
        self.db.commit()

        return volunteer

    # === Profile Management ===

    def get_volunteer(self, volunteer_id: int) -> Optional[Volunteer]:
        """Gönüllü detayı"""
        return self.db.query(Volunteer).filter(
            Volunteer.id == volunteer_id
        ).first()

    def get_volunteer_by_email(self, email: str) -> Optional[Volunteer]:
        """Email ile gönüllü bul"""
        return self.db.query(Volunteer).filter(
            Volunteer.email == email
        ).first()

    def update_volunteer_profile(
        self,
        volunteer_id: int,
        data: VolunteerProfileUpdate
    ) -> Volunteer:
        """Profil güncelleme"""
        volunteer = self.get_volunteer(volunteer_id)
        if not volunteer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gönüllü bulunamadı"
            )

        # Güncelle
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(volunteer, field, value)

        volunteer.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(volunteer)

        return volunteer

    def upload_profile_photo(
        self,
        volunteer_id: int,
        file: UploadFile
    ) -> str:
        """Profil fotoğrafı yükleme"""
        volunteer = self.get_volunteer(volunteer_id)
        if not volunteer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gönüllü bulunamadı"
            )

        # Dosya uzantısı kontrolü
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Sadece şu formatlar desteklenir: {', '.join(allowed_extensions)}"
            )

        # Dosya adı oluştur
        filename = f"volunteer_{volunteer_id}_{uuid.uuid4()}{file_ext}"
        upload_dir = "uploads/volunteers"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)

        # Dosyayı kaydet
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        # URL oluştur
        photo_url = f"/{file_path}"

        # Eski fotoğrafı sil
        if volunteer.profile_photo and os.path.exists(volunteer.profile_photo.lstrip('/')):
            try:
                os.remove(volunteer.profile_photo.lstrip('/'))
            except:
                pass

        # Veritabanını güncelle
        volunteer.profile_photo = photo_url
        self.db.commit()

        return photo_url

    # === Skills Management ===

    def add_volunteer_skill(
        self,
        volunteer_id: int,
        skill_data: VolunteerSkillAdd
    ) -> Volunteer:
        """Gönüllüye yetkinlik ekle"""
        volunteer = self.get_volunteer(volunteer_id)
        if not volunteer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gönüllü bulunamadı"
            )

        # Yetkinlik var mı?
        skill = self.db.query(Skill).filter(Skill.id == skill_data.skill_id).first()
        if not skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Yetkinlik bulunamadı"
            )

        # Zaten ekli mi?
        existing = self.db.query(volunteer_skills).filter(
            and_(
                volunteer_skills.c.volunteer_id == volunteer_id,
                volunteer_skills.c.skill_id == skill_data.skill_id
            )
        ).first()

        if existing:
            # Güncelle
            self.db.execute(
                volunteer_skills.update().where(
                    and_(
                        volunteer_skills.c.volunteer_id == volunteer_id,
                        volunteer_skills.c.skill_id == skill_data.skill_id
                    )
                ).values(
                    proficiency_level=skill_data.proficiency_level,
                    certified=skill_data.certified,
                    certificate_date=skill_data.certificate_date
                )
            )
        else:
            # Ekle
            self.db.execute(
                volunteer_skills.insert().values(
                    volunteer_id=volunteer_id,
                    skill_id=skill_data.skill_id,
                    proficiency_level=skill_data.proficiency_level,
                    certified=skill_data.certified,
                    certificate_date=skill_data.certificate_date
                )
            )

        self.db.commit()
        self.db.refresh(volunteer)

        return volunteer

    def remove_volunteer_skill(self, volunteer_id: int, skill_id: int) -> Volunteer:
        """Gönüllüden yetkinlik çıkar"""
        volunteer = self.get_volunteer(volunteer_id)
        if not volunteer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gönüllü bulunamadı"
            )

        self.db.execute(
            volunteer_skills.delete().where(
                and_(
                    volunteer_skills.c.volunteer_id == volunteer_id,
                    volunteer_skills.c.skill_id == skill_id
                )
            )
        )

        self.db.commit()
        self.db.refresh(volunteer)

        return volunteer

    # === List & Search ===

    def list_volunteers(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[VolunteerStatus] = None,
        city: Optional[str] = None,
        is_approved: Optional[bool] = None,
        skill_id: Optional[int] = None
    ) -> List[Volunteer]:
        """Gönüllü listesi"""
        query = self.db.query(Volunteer)

        # Filtreler
        if status:
            query = query.filter(Volunteer.status == status)
        if city:
            query = query.filter(Volunteer.city == city)
        if is_approved is not None:
            query = query.filter(Volunteer.is_approved == is_approved)
        if skill_id:
            query = query.join(volunteer_skills).filter(
                volunteer_skills.c.skill_id == skill_id
            )

        query = query.offset(skip).limit(limit)
        return query.all()

    def get_volunteer_stats(self) -> VolunteerStats:
        """Gönüllü istatistikleri"""
        total = self.db.query(func.count(Volunteer.id)).scalar() or 0
        active = self.db.query(func.count(Volunteer.id)).filter(
            Volunteer.status == VolunteerStatus.ACTIVE
        ).scalar() or 0
        on_duty = self.db.query(func.count(Volunteer.id)).filter(
            Volunteer.status == VolunteerStatus.ON_DUTY
        ).scalar() or 0

        total_missions = self.db.query(func.sum(Volunteer.completed_missions)).scalar() or 0
        total_hours = self.db.query(func.sum(Volunteer.total_hours)).scalar() or 0.0
        avg_rating = self.db.query(func.avg(Volunteer.rating)).scalar() or 0.0

        return VolunteerStats(
            total_volunteers=total,
            active_volunteers=active,
            on_duty_volunteers=on_duty,
            total_missions_completed=total_missions,
            total_hours=total_hours,
            avg_rating=round(avg_rating, 2)
        )

    # === Admin Operations ===

    def approve_volunteer(self, volunteer_id: int, approved: bool = True) -> Volunteer:
        """Gönüllü onaylama"""
        volunteer = self.get_volunteer(volunteer_id)
        if not volunteer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gönüllü bulunamadı"
            )

        volunteer.is_approved = approved
        self.db.commit()
        self.db.refresh(volunteer)

        return volunteer

    def change_volunteer_status(
        self,
        volunteer_id: int,
        new_status: VolunteerStatus
    ) -> Volunteer:
        """Gönüllü durumu değiştir"""
        volunteer = self.get_volunteer(volunteer_id)
        if not volunteer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gönüllü bulunamadı"
            )

        volunteer.status = new_status
        self.db.commit()
        self.db.refresh(volunteer)

        return volunteer
