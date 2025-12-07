"""
Afet Çağrısı servisi
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status
from datetime import datetime
from typing import List, Optional

from ..models.disaster_call import (
    DisasterCall,
    DisasterCallSkill,
    VolunteerAssignment,
    DisasterCallStatus,
    VolunteerAssignmentStatus,
    VolunteerNotification
)
from ..models.disaster import Disaster
from ..models.volunteer import Volunteer, VolunteerStatus
from ..schemas.disaster_call import (
    DisasterCallCreate,
    DisasterCallUpdate,
    VolunteerMatchingRequest,
    MatchedVolunteer,
    VolunteerMatchingResponse
)
from .matching_algorithm import VolunteerMatchingAlgorithm


class DisasterCallService:
    """Afet çağrısı yönetim servisi"""

    def __init__(self, db: Session):
        self.db = db
        self.matching_algo = VolunteerMatchingAlgorithm(db)

    # === CRUD Operations ===

    def create_disaster_call(
        self,
        data: DisasterCallCreate,
        created_by: int
    ) -> DisasterCall:
        """Yeni afet çağrısı oluştur"""
        # Afet var mı kontrol et
        disaster = self.db.query(Disaster).filter(
            Disaster.id == data.disaster_id
        ).first()

        if not disaster:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Afet bulunamadı"
            )

        # Çağrı oluştur
        disaster_call = DisasterCall(
            disaster_id=data.disaster_id,
            title=data.title,
            description=data.description,
            required_volunteers=data.required_volunteers,
            priority=data.priority,
            estimated_duration=data.estimated_duration,
            start_time=data.start_time,
            end_time=data.end_time,
            assembly_point_id=data.assembly_point_id,
            meeting_instructions=data.meeting_instructions,
            location=data.location,
            latitude=data.latitude,
            longitude=data.longitude,
            equipment_needed=data.equipment_needed,
            special_instructions=data.special_instructions,
            created_by=created_by,
            status=DisasterCallStatus.DRAFT
        )

        self.db.add(disaster_call)
        self.db.flush()

        # Gerekli yetkinlikleri ekle
        for skill_data in data.required_skills:
            call_skill = DisasterCallSkill(
                disaster_call_id=disaster_call.id,
                skill_id=skill_data.skill_id,
                required_count=skill_data.required_count,
                min_proficiency=skill_data.min_proficiency,
                is_mandatory=skill_data.is_mandatory
            )
            self.db.add(call_skill)

        self.db.commit()
        self.db.refresh(disaster_call)

        return disaster_call

    def get_disaster_call(self, call_id: int) -> Optional[DisasterCall]:
        """Afet çağrısı detayı"""
        return self.db.query(DisasterCall).filter(
            DisasterCall.id == call_id
        ).first()

    def update_disaster_call(
        self,
        call_id: int,
        data: DisasterCallUpdate
    ) -> DisasterCall:
        """Afet çağrısı güncelle"""
        disaster_call = self.get_disaster_call(call_id)
        if not disaster_call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Afet çağrısı bulunamadı"
            )

        # Güncelle
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(disaster_call, field, value)

        disaster_call.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(disaster_call)

        return disaster_call

    def activate_disaster_call(self, call_id: int) -> DisasterCall:
        """Afet çağrısını aktif et"""
        disaster_call = self.get_disaster_call(call_id)
        if not disaster_call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Afet çağrısı bulunamadı"
            )

        disaster_call.status = DisasterCallStatus.ACTIVE
        disaster_call.activated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(disaster_call)

        return disaster_call

    def list_disaster_calls(
        self,
        disaster_id: Optional[int] = None,
        status: Optional[DisasterCallStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[DisasterCall]:
        """Afet çağrıları listesi"""
        query = self.db.query(DisasterCall)

        if disaster_id:
            query = query.filter(DisasterCall.disaster_id == disaster_id)
        if status:
            query = query.filter(DisasterCall.status == status)

        query = query.order_by(DisasterCall.created_at.desc())
        query = query.offset(skip).limit(limit)

        return query.all()

    # === Matching & Assignment ===

    def match_volunteers(
        self,
        request: VolunteerMatchingRequest
    ) -> VolunteerMatchingResponse:
        """
        Bir afet çağrısı için en uygun gönüllüleri bul.
        """
        disaster_call = self.get_disaster_call(request.disaster_call_id)
        if not disaster_call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Afet çağrısı bulunamadı"
            )

        # Eşleştirme algoritmasını çalıştır
        matched = self.matching_algo.find_best_matches(
            disaster_call_id=request.disaster_call_id,
            max_distance_km=request.max_distance_km,
            limit=disaster_call.required_volunteers * 2  # Fazladan getir
        )

        # Response formatı
        matched_volunteers = []
        for volunteer, score, distance in matched:
            # Gönüllünün yetkinliklerini al
            volunteer_skills = [skill.name for skill in volunteer.skills]

            matched_volunteers.append(
                MatchedVolunteer(
                    volunteer_id=volunteer.id,
                    first_name=volunteer.first_name,
                    last_name=volunteer.last_name,
                    email=volunteer.email,
                    phone=volunteer.phone,
                    profile_photo=volunteer.profile_photo,
                    match_score=round(score, 2),
                    distance_km=round(distance, 2) if distance else None,
                    matched_skills=volunteer_skills,
                    status=volunteer.status.value,
                    rating=volunteer.rating,
                    total_missions=volunteer.total_missions
                )
            )

        # Otomatik atama
        if request.auto_assign:
            for matched_vol in matched_volunteers[:disaster_call.required_volunteers]:
                self.assign_volunteer(
                    disaster_call_id=request.disaster_call_id,
                    volunteer_id=matched_vol.volunteer_id,
                    match_score=matched_vol.match_score,
                    distance_km=matched_vol.distance_km,
                    auto_notify=request.auto_notify
                )

        return VolunteerMatchingResponse(
            disaster_call_id=request.disaster_call_id,
            required_volunteers=disaster_call.required_volunteers,
            matched_volunteers=matched_volunteers,
            total_matched=len(matched_volunteers)
        )

    def assign_volunteer(
        self,
        disaster_call_id: int,
        volunteer_id: int,
        match_score: float = 0.0,
        distance_km: Optional[float] = None,
        auto_notify: bool = True
    ) -> VolunteerAssignment:
        """Gönüllü atama"""
        # Zaten atanmış mı?
        existing = self.db.query(VolunteerAssignment).filter(
            and_(
                VolunteerAssignment.disaster_call_id == disaster_call_id,
                VolunteerAssignment.volunteer_id == volunteer_id
            )
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu gönüllü zaten atanmış"
            )

        # Atama oluştur
        assignment = VolunteerAssignment(
            disaster_call_id=disaster_call_id,
            volunteer_id=volunteer_id,
            match_score=match_score,
            distance_km=distance_km,
            status=VolunteerAssignmentStatus.PENDING
        )

        self.db.add(assignment)
        self.db.flush()

        # Disaster call sayaçlarını güncelle
        disaster_call = self.get_disaster_call(disaster_call_id)
        disaster_call.assigned_volunteers += 1

        # Bildirim gönder
        if auto_notify:
            self._send_assignment_notification(assignment)

        self.db.commit()
        self.db.refresh(assignment)

        return assignment

    def respond_to_assignment(
        self,
        assignment_id: int,
        volunteer_id: int,
        accept: bool,
        notes: Optional[str] = None
    ) -> VolunteerAssignment:
        """Gönüllü atamaya cevap verir (kabul/red)"""
        assignment = self.db.query(VolunteerAssignment).filter(
            VolunteerAssignment.id == assignment_id
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Atama bulunamadı"
            )

        if assignment.volunteer_id != volunteer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu atamaya yanıt verme yetkiniz yok"
            )

        # Durumu güncelle
        if accept:
            assignment.status = VolunteerAssignmentStatus.ACCEPTED
            # Gönüllü durumunu güncelle
            volunteer = self.db.query(Volunteer).filter(
                Volunteer.id == volunteer_id
            ).first()
            if volunteer:
                volunteer.status = VolunteerStatus.ON_DUTY

            # Disaster call sayacını güncelle
            disaster_call = self.get_disaster_call(assignment.disaster_call_id)
            disaster_call.accepted_volunteers += 1
        else:
            assignment.status = VolunteerAssignmentStatus.REJECTED

        assignment.responded_at = datetime.utcnow()
        assignment.volunteer_notes = notes

        self.db.commit()
        self.db.refresh(assignment)

        return assignment

    def get_volunteer_assignments(
        self,
        volunteer_id: int,
        status: Optional[VolunteerAssignmentStatus] = None
    ) -> List[VolunteerAssignment]:
        """Gönüllünün atamalarını getir"""
        query = self.db.query(VolunteerAssignment).filter(
            VolunteerAssignment.volunteer_id == volunteer_id
        )

        if status:
            query = query.filter(VolunteerAssignment.status == status)

        query = query.order_by(VolunteerAssignment.assigned_at.desc())

        return query.all()

    def get_call_assignments(
        self,
        disaster_call_id: int,
        status: Optional[VolunteerAssignmentStatus] = None
    ) -> List[VolunteerAssignment]:
        """Afet çağrısının atamalarını getir"""
        query = self.db.query(VolunteerAssignment).filter(
            VolunteerAssignment.disaster_call_id == disaster_call_id
        )

        if status:
            query = query.filter(VolunteerAssignment.status == status)

        return query.all()

    # === Notifications ===

    def _send_assignment_notification(self, assignment: VolunteerAssignment):
        """Atama bildirimi gönder"""
        disaster_call = self.get_disaster_call(assignment.disaster_call_id)

        notification = VolunteerNotification(
            volunteer_id=assignment.volunteer_id,
            title="🚨 Yeni Afet Çağrısı",
            message=f"{disaster_call.title} - Acil gönüllü desteği gerekiyor!",
            notification_type="disaster_call",
            disaster_call_id=disaster_call.id,
            assignment_id=assignment.id,
            is_read=False,
            is_sent=False
        )

        self.db.add(notification)
        assignment.notified_at = datetime.utcnow()
        self.db.commit()

        # TODO: Gerçek push notification gönder (Firebase, OneSignal vb.)

    def send_broadcast_notification(
        self,
        disaster_call_id: int,
        title: str,
        message: str
    ):
        """Tüm atanan gönüllülere toplu bildirim gönder"""
        assignments = self.get_call_assignments(disaster_call_id)

        for assignment in assignments:
            notification = VolunteerNotification(
                volunteer_id=assignment.volunteer_id,
                title=title,
                message=message,
                notification_type="broadcast",
                disaster_call_id=disaster_call_id,
                is_read=False,
                is_sent=False
            )
            self.db.add(notification)

        self.db.commit()

        # TODO: Gerçek push notification gönder
