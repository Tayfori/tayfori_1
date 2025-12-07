"""
Afet Çağrısı şemaları
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DisasterCallStatusEnum(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class VolunteerAssignmentStatusEnum(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    ARRIVED = "arrived"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# === Disaster Call Skill ===
class DisasterCallSkillCreate(BaseModel):
    skill_id: int
    required_count: int = 1
    min_proficiency: int = Field(ge=1, le=5, default=1)
    is_mandatory: bool = False


class DisasterCallSkillResponse(BaseModel):
    id: int
    skill_id: int
    skill_name: str
    required_count: int
    assigned_count: int
    min_proficiency: int
    is_mandatory: bool

    class Config:
        from_attributes = True


# === Disaster Call ===
class DisasterCallCreate(BaseModel):
    disaster_id: int
    title: str
    description: Optional[str] = None
    required_volunteers: int = Field(gt=0)
    priority: str = Field(default="medium")  # low, medium, high, critical
    estimated_duration: Optional[float] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    assembly_point_id: Optional[int] = None
    meeting_instructions: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    equipment_needed: Optional[str] = None
    special_instructions: Optional[str] = None
    required_skills: List[DisasterCallSkillCreate] = []


class DisasterCallUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    required_volunteers: Optional[int] = None
    priority: Optional[str] = None
    estimated_duration: Optional[float] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    assembly_point_id: Optional[int] = None
    meeting_instructions: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    equipment_needed: Optional[str] = None
    special_instructions: Optional[str] = None
    status: Optional[DisasterCallStatusEnum] = None


class DisasterCallResponse(BaseModel):
    id: int
    disaster_id: int
    title: str
    description: Optional[str] = None
    required_volunteers: int
    assigned_volunteers: int
    accepted_volunteers: int
    priority: str
    estimated_duration: Optional[float] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    assembly_point_id: Optional[int] = None
    meeting_instructions: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    equipment_needed: Optional[str] = None
    special_instructions: Optional[str] = None
    status: DisasterCallStatusEnum
    created_by: int
    created_at: datetime
    updated_at: datetime
    activated_at: Optional[datetime] = None
    required_skills: List[DisasterCallSkillResponse] = []

    class Config:
        from_attributes = True


# === Volunteer Assignment ===
class VolunteerAssignmentCreate(BaseModel):
    disaster_call_id: int
    volunteer_id: int
    match_score: Optional[float] = 0.0
    distance_km: Optional[float] = None


class VolunteerAssignmentUpdate(BaseModel):
    status: Optional[VolunteerAssignmentStatusEnum] = None
    volunteer_notes: Optional[str] = None
    coordinator_notes: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)


class VolunteerAssignmentResponse(BaseModel):
    id: int
    disaster_call_id: int
    volunteer_id: int
    volunteer_name: str
    volunteer_phone: str
    volunteer_photo: Optional[str] = None
    status: VolunteerAssignmentStatusEnum
    match_score: float
    distance_km: Optional[float] = None
    assigned_at: datetime
    notified_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None
    arrived_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    volunteer_notes: Optional[str] = None
    coordinator_notes: Optional[str] = None
    rating: Optional[int] = None

    class Config:
        from_attributes = True


# === Matching Request ===
class VolunteerMatchingRequest(BaseModel):
    """Gönüllü eşleştirme isteği"""
    disaster_call_id: int
    max_distance_km: Optional[float] = 50.0  # Maksimum uzaklık (km)
    auto_assign: bool = False  # Otomatik atama yap
    auto_notify: bool = True  # Otomatik bildirim gönder


class MatchedVolunteer(BaseModel):
    """Eşleşen gönüllü"""
    volunteer_id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    profile_photo: Optional[str] = None
    match_score: float  # 0-100
    distance_km: Optional[float] = None
    matched_skills: List[str] = []
    status: str
    rating: float
    total_missions: int


class VolunteerMatchingResponse(BaseModel):
    """Eşleştirme sonucu"""
    disaster_call_id: int
    required_volunteers: int
    matched_volunteers: List[MatchedVolunteer]
    total_matched: int
