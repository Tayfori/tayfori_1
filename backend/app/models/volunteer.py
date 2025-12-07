from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Table, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..database import Base


class BloodType(enum.Enum):
    """Kan grubu tipleri"""
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"


class VolunteerStatus(enum.Enum):
    """Gönüllü durumu"""
    ACTIVE = "active"  # Aktif
    INACTIVE = "inactive"  # Pasif
    ON_DUTY = "on_duty"  # Görevde
    UNAVAILABLE = "unavailable"  # Müsait değil


# Gönüllü - Yetkinlik ilişki tablosu (Many-to-Many)
volunteer_skills = Table(
    'volunteer_skills',
    Base.metadata,
    Column('volunteer_id', Integer, ForeignKey('volunteers.id', ondelete='CASCADE')),
    Column('skill_id', Integer, ForeignKey('skills.id', ondelete='CASCADE')),
    Column('proficiency_level', Integer, default=1),  # 1-5 arası yetkinlik seviyesi
    Column('certified', Boolean, default=False),  # Sertifikalı mı?
    Column('certificate_date', DateTime, nullable=True),  # Sertifika tarihi
    Column('created_at', DateTime, default=datetime.utcnow)
)


class Volunteer(Base):
    """Gönüllü modeli"""
    __tablename__ = 'volunteers'

    id = Column(Integer, primary_key=True, index=True)

    # Kimlik Bilgileri
    tc_no = Column(String(11), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=False)
    password_hash = Column(String(255), nullable=False)

    # Kişisel Bilgiler
    birth_date = Column(DateTime, nullable=True)
    gender = Column(String(10), nullable=True)  # Erkek, Kadın, Diğer
    blood_type = Column(SQLEnum(BloodType), nullable=True)

    # Profil Bilgileri
    profile_photo = Column(String(500), nullable=True)  # Fotoğraf URL
    bio = Column(Text, nullable=True)  # Kısa biyografi
    occupation = Column(String(200), nullable=True)  # Meslek
    education_level = Column(String(100), nullable=True)  # Eğitim durumu

    # Konum Bilgileri
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=False)
    district = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Acil Durum İletişim
    emergency_contact_name = Column(String(200), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    emergency_contact_relation = Column(String(100), nullable=True)

    # Sağlık Bilgileri
    health_conditions = Column(Text, nullable=True)  # Kronik hastalıklar
    medications = Column(Text, nullable=True)  # Kullandığı ilaçlar
    allergies = Column(Text, nullable=True)  # Alerjiler

    # Kullanılabilirlik
    status = Column(SQLEnum(VolunteerStatus), default=VolunteerStatus.ACTIVE)
    availability_notes = Column(Text, nullable=True)  # Müsaitlik notları

    # İstatistikler
    total_missions = Column(Integer, default=0)  # Toplam görev sayısı
    completed_missions = Column(Integer, default=0)  # Tamamlanan görev sayısı
    total_hours = Column(Float, default=0.0)  # Toplam gönüllülük saati
    rating = Column(Float, default=5.0)  # Ortalama değerlendirme (1-5)

    # Sistem
    is_verified = Column(Boolean, default=False)  # Email doğrulandı mı?
    is_approved = Column(Boolean, default=False)  # Yönetici onayı
    notification_enabled = Column(Boolean, default=True)  # Bildirim almak istiyor mu?
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # İlişkiler
    skills = relationship('Skill', secondary=volunteer_skills, back_populates='volunteers')
    assignments = relationship('VolunteerAssignment', back_populates='volunteer', cascade='all, delete-orphan')
    notifications = relationship('Notification', back_populates='volunteer', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Volunteer {self.first_name} {self.last_name} ({self.email})>"


class Skill(Base):
    """Yetkinlik modeli"""
    __tablename__ = 'skills'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # Kategori (Tıbbi, Teknik, Lojistik vb.)
    icon = Column(String(100), nullable=True)  # İkon emoji veya class
    is_critical = Column(Boolean, default=False)  # Kritik yetkinlik mi?
    created_at = Column(DateTime, default=datetime.utcnow)

    # İlişkiler
    volunteers = relationship('Volunteer', secondary=volunteer_skills, back_populates='skills')
    disaster_calls = relationship('DisasterCallSkill', back_populates='skill', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Skill {self.name}>"


class AssemblyPoint(Base):
    """Toplanma noktası modeli"""
    __tablename__ = 'assembly_points'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Konum
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    district = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # Özellikler
    capacity = Column(Integer, nullable=True)  # Kapasite
    facilities = Column(Text, nullable=True)  # Olanaklar (JSON string)
    contact_person = Column(String(200), nullable=True)
    contact_phone = Column(String(20), nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<AssemblyPoint {self.name}>"
