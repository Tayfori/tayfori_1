from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base


class DisasterCallStatus(enum.Enum):
    """Afet çağrısı durumu"""
    DRAFT = "draft"  # Taslak
    ACTIVE = "active"  # Aktif - Gönüllüler çağrılıyor
    IN_PROGRESS = "in_progress"  # Devam ediyor
    COMPLETED = "completed"  # Tamamlandı
    CANCELLED = "cancelled"  # İptal edildi


class VolunteerAssignmentStatus(enum.Enum):
    """Gönüllü atama durumu"""
    PENDING = "pending"  # Bekliyor - Bildirim gönderildi
    ACCEPTED = "accepted"  # Kabul edildi
    REJECTED = "rejected"  # Reddedildi
    ARRIVED = "arrived"  # Toplanma noktasına ulaştı
    COMPLETED = "completed"  # Görevi tamamladı
    CANCELLED = "cancelled"  # İptal edildi


class DisasterCall(Base):
    """Afet çağrısı modeli - Bir afet için gönüllü çağrısı"""
    __tablename__ = 'disaster_calls'

    id = Column(Integer, primary_key=True, index=True)

    # Afet bilgisi
    disaster_id = Column(Integer, ForeignKey('disasters.id', ondelete='CASCADE'), nullable=False)

    # Çağrı bilgileri
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    required_volunteers = Column(Integer, nullable=False)  # Kaç gönüllü gerekiyor
    assigned_volunteers = Column(Integer, default=0)  # Kaç gönüllü atandı
    accepted_volunteers = Column(Integer, default=0)  # Kaç gönüllü kabul etti

    # Öncelik ve süre
    priority = Column(String(20), default='medium')  # low, medium, high, critical
    estimated_duration = Column(Float, nullable=True)  # Tahmini süre (saat)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)

    # Toplanma noktası
    assembly_point_id = Column(Integer, ForeignKey('assembly_points.id'), nullable=True)
    meeting_instructions = Column(Text, nullable=True)  # Toplanma talimatları

    # Konum (afetten farklı olabilir)
    location = Column(String(500), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Durum
    status = Column(SQLEnum(DisasterCallStatus), default=DisasterCallStatus.DRAFT)

    # Notlar
    equipment_needed = Column(Text, nullable=True)  # Gerekli ekipman
    special_instructions = Column(Text, nullable=True)  # Özel talimatlar

    # Oluşturan
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activated_at = Column(DateTime, nullable=True)  # Aktif hale getirilme zamanı

    # İlişkiler
    disaster = relationship('Disaster', back_populates='calls')
    assembly_point = relationship('AssemblyPoint')
    creator = relationship('User')
    required_skills = relationship('DisasterCallSkill', back_populates='disaster_call', cascade='all, delete-orphan')
    assignments = relationship('VolunteerAssignment', back_populates='disaster_call', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<DisasterCall {self.title} ({self.status.value})>"


class DisasterCallSkill(Base):
    """Afet çağrısında aranan yetkinlikler"""
    __tablename__ = 'disaster_call_skills'

    id = Column(Integer, primary_key=True, index=True)
    disaster_call_id = Column(Integer, ForeignKey('disaster_calls.id', ondelete='CASCADE'), nullable=False)
    skill_id = Column(Integer, ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)

    required_count = Column(Integer, default=1)  # Bu yetkinlikten kaç kişi gerekiyor
    assigned_count = Column(Integer, default=0)  # Kaç kişi atandı
    min_proficiency = Column(Integer, default=1)  # Minimum yetkinlik seviyesi (1-5)
    is_mandatory = Column(Boolean, default=False)  # Zorunlu mu?

    created_at = Column(DateTime, default=datetime.utcnow)

    # İlişkiler
    disaster_call = relationship('DisasterCall', back_populates='required_skills')
    skill = relationship('Skill', back_populates='disaster_calls')

    def __repr__(self):
        return f"<DisasterCallSkill {self.skill.name} x{self.required_count}>"


class VolunteerAssignment(Base):
    """Gönüllü atama modeli - Bir gönüllünün bir afet çağrısına ataması"""
    __tablename__ = 'volunteer_assignments'

    id = Column(Integer, primary_key=True, index=True)

    disaster_call_id = Column(Integer, ForeignKey('disaster_calls.id', ondelete='CASCADE'), nullable=False)
    volunteer_id = Column(Integer, ForeignKey('volunteers.id', ondelete='CASCADE'), nullable=False)

    # Durum
    status = Column(SQLEnum(VolunteerAssignmentStatus), default=VolunteerAssignmentStatus.PENDING)

    # Eşleştirme skoru (algoritma tarafından hesaplanan)
    match_score = Column(Float, default=0.0)  # 0-100 arası
    distance_km = Column(Float, nullable=True)  # Gönüllünün uzaklığı (km)

    # Zaman damgaları
    assigned_at = Column(DateTime, default=datetime.utcnow)
    notified_at = Column(DateTime, nullable=True)
    responded_at = Column(DateTime, nullable=True)
    arrived_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Geri bildirim
    volunteer_notes = Column(Text, nullable=True)  # Gönüllünün notları
    coordinator_notes = Column(Text, nullable=True)  # Koordinatörün notları
    rating = Column(Integer, nullable=True)  # Gönüllü değerlendirmesi (1-5)

    # İlişkiler
    disaster_call = relationship('DisasterCall', back_populates='assignments')
    volunteer = relationship('Volunteer', back_populates='assignments')

    def __repr__(self):
        return f"<VolunteerAssignment {self.volunteer.first_name} - {self.disaster_call.title} ({self.status.value})>"


class VolunteerNotification(Base):
    """Gönüllü bildirim modeli"""
    __tablename__ = 'volunteer_notifications'

    id = Column(Integer, primary_key=True, index=True)

    volunteer_id = Column(Integer, ForeignKey('volunteers.id', ondelete='CASCADE'), nullable=False)

    # Bildirim içeriği
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # disaster_call, assignment, system, etc.

    # İlişkili kayıt
    disaster_call_id = Column(Integer, ForeignKey('disaster_calls.id', ondelete='SET NULL'), nullable=True)
    assignment_id = Column(Integer, ForeignKey('volunteer_assignments.id', ondelete='SET NULL'), nullable=True)

    # Durum
    is_read = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)  # Push notification gönderildi mi?

    # Zaman
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)

    # İlişkiler
    volunteer = relationship('Volunteer', back_populates='notifications')

    def __repr__(self):
        return f"<VolunteerNotification {self.title} - {self.volunteer.email}>"
