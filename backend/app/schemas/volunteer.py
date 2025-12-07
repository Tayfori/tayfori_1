"""
Gönüllü şemaları (Pydantic models)
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class BloodTypeEnum(str, Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"


class VolunteerStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_DUTY = "on_duty"
    UNAVAILABLE = "unavailable"


# === Skill Schemas ===
class SkillBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    icon: Optional[str] = None
    is_critical: bool = False


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    icon: Optional[str] = None
    is_critical: Optional[bool] = None


class Skill(SkillBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# === Volunteer Skill ===
class VolunteerSkillAdd(BaseModel):
    skill_id: int
    proficiency_level: int = Field(ge=1, le=5, default=1)
    certified: bool = False
    certificate_date: Optional[datetime] = None


class VolunteerSkillResponse(BaseModel):
    skill: Skill
    proficiency_level: int
    certified: bool
    certificate_date: Optional[datetime] = None

    class Config:
        from_attributes = True


# === Assembly Point Schemas ===
class AssemblyPointBase(BaseModel):
    name: str
    description: Optional[str] = None
    address: str
    city: str
    district: Optional[str] = None
    latitude: float
    longitude: float
    capacity: Optional[int] = None
    facilities: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None


class AssemblyPointCreate(AssemblyPointBase):
    pass


class AssemblyPointUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    capacity: Optional[int] = None
    facilities: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    is_active: Optional[bool] = None


class AssemblyPoint(AssemblyPointBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# === Volunteer Schemas ===
class VolunteerRegister(BaseModel):
    """Gönüllü kayıt (dışarıdan kayıt için)"""
    tc_no: str = Field(min_length=11, max_length=11)
    first_name: str = Field(min_length=2, max_length=100)
    last_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str
    password: str = Field(min_length=6)
    city: str
    district: Optional[str] = None
    address: Optional[str] = None
    birth_date: Optional[datetime] = None
    gender: Optional[str] = None

    @validator('tc_no')
    def validate_tc(cls, v):
        if not v.isdigit():
            raise ValueError('TC kimlik numarası sadece rakamlardan oluşmalıdır')
        return v


class VolunteerLogin(BaseModel):
    """Gönüllü giriş"""
    email: EmailStr
    password: str


class VolunteerProfileUpdate(BaseModel):
    """Profil güncelleme"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    birth_date: Optional[datetime] = None
    gender: Optional[str] = None
    blood_type: Optional[BloodTypeEnum] = None
    bio: Optional[str] = None
    occupation: Optional[str] = None
    education_level: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    health_conditions: Optional[str] = None
    medications: Optional[str] = None
    allergies: Optional[str] = None
    availability_notes: Optional[str] = None
    notification_enabled: Optional[bool] = None


class VolunteerResponse(BaseModel):
    """Gönüllü detay response"""
    id: int
    tc_no: str
    first_name: str
    last_name: str
    email: str
    phone: str
    birth_date: Optional[datetime] = None
    gender: Optional[str] = None
    blood_type: Optional[BloodTypeEnum] = None
    profile_photo: Optional[str] = None
    bio: Optional[str] = None
    occupation: Optional[str] = None
    education_level: Optional[str] = None
    address: Optional[str] = None
    city: str
    district: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    health_conditions: Optional[str] = None
    medications: Optional[str] = None
    allergies: Optional[str] = None
    status: VolunteerStatusEnum
    availability_notes: Optional[str] = None
    total_missions: int
    completed_missions: int
    total_hours: float
    rating: float
    is_verified: bool
    is_approved: bool
    notification_enabled: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    skills: List[VolunteerSkillResponse] = []

    class Config:
        from_attributes = True


class VolunteerListResponse(BaseModel):
    """Gönüllü liste response (özet bilgi)"""
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    city: str
    district: Optional[str] = None
    profile_photo: Optional[str] = None
    status: VolunteerStatusEnum
    total_missions: int
    rating: float
    is_approved: bool
    created_at: datetime

    class Config:
        from_attributes = True


class VolunteerAuthResponse(BaseModel):
    """Giriş sonrası response"""
    access_token: str
    token_type: str = "bearer"
    volunteer: VolunteerResponse


class VolunteerStats(BaseModel):
    """Gönüllü istatistikleri"""
    total_volunteers: int
    active_volunteers: int
    on_duty_volunteers: int
    total_missions_completed: int
    total_hours: float
    avg_rating: float
