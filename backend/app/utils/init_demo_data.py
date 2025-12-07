"""
Demo verileri oluşturma scripti
"""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from passlib.context import CryptContext

from ..models.volunteer import Volunteer, Skill, AssemblyPoint, VolunteerStatus, BloodType, volunteer_skills
from ..models.disaster import Disaster, DisasterType, DisasterSeverity, DisasterStatus
from ..models.disaster_call import DisasterCall, DisasterCallSkill, DisasterCallStatus

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_demo_skills(db: Session):
    """Demo yetkinlikler oluştur"""
    skills_data = [
        {"name": "İlk Yardım", "description": "Temel ilk yardım bilgisi", "category": "Tıbbi", "icon": "🏥", "is_critical": True},
        {"name": "Arama-Kurtarma", "description": "Enkaz altında arama-kurtarma", "category": "Teknik", "icon": "🔍", "is_critical": True},
        {"name": "Psikososyal Destek", "description": "Psikolojik destek", "category": "Sosyal", "icon": "🤝", "is_critical": False},
        {"name": "Lojistik", "description": "Malzeme taşıma ve dağıtım", "category": "Lojistik", "icon": "📦", "is_critical": False},
        {"name": "İletişim", "description": "Telsiz ve haberleşme", "category": "Teknik", "icon": "📡", "is_critical": False},
        {"name": "Su Kurtarma", "description": "Sel ve su altı kurtarma", "category": "Teknik", "icon": "🌊", "is_critical": True},
        {"name": "Yangın Söndürme", "description": "Yangın müdahale", "category": "Teknik", "icon": "🚒", "is_critical": True},
        {"name": "Çevirmenlik", "description": "Yabancı dil desteği", "category": "Sosyal", "icon": "🌍", "is_critical": False},
        {"name": "Sağlık Personeli", "description": "Doktor, hemşire, paramedik", "category": "Tıbbi", "icon": "⚕️", "is_critical": True},
        {"name": "Mutfak", "description": "Toplu yemek hazırlama", "category": "Lojistik", "icon": "🍳", "is_critical": False},
    ]

    skills = []
    for skill_data in skills_data:
        existing = db.query(Skill).filter(Skill.name == skill_data["name"]).first()
        if not existing:
            skill = Skill(**skill_data)
            db.add(skill)
            db.flush()
            skills.append(skill)
        else:
            skills.append(existing)

    db.commit()
    print(f"✓ {len(skills)} yetkinlik oluşturuldu")
    return skills


def create_demo_assembly_points(db: Session):
    """Demo toplanma noktaları oluştur"""
    points_data = [
        {
            "name": "Ankara Stadyumu",
            "description": "Ana toplanma merkezi",
            "address": "Eryaman, Ankara",
            "city": "Ankara",
            "district": "Etimesgut",
            "latitude": 39.9334,
            "longitude": 32.8597,
            "capacity": 5000,
            "facilities": "Çadır, Yemek, Sağlık",
            "contact_person": "Mehmet Yılmaz",
            "contact_phone": "0555 111 11 11"
        },
        {
            "name": "İstanbul Ataköy Toplanma Alanı",
            "description": "Sahil bölgesi toplanma",
            "address": "Ataköy, İstanbul",
            "city": "İstanbul",
            "district": "Bakırköy",
            "latitude": 40.9849,
            "longitude": 28.8594,
            "capacity": 3000,
            "facilities": "Çadır, İletişim Merkezi",
            "contact_person": "Ayşe Demir",
            "contact_phone": "0555 222 22 22"
        },
        {
            "name": "Hatay Antakya Stadı",
            "description": "Deprem sonrası ana merkez",
            "address": "Antakya Merkez",
            "city": "Hatay",
            "district": "Antakya",
            "latitude": 36.2022,
            "longitude": 36.1604,
            "capacity": 10000,
            "facilities": "Hastane, Çadır, Yemek, Güvenlik",
            "contact_person": "Ali Kaya",
            "contact_phone": "0555 333 33 33"
        }
    ]

    points = []
    for point_data in points_data:
        existing = db.query(AssemblyPoint).filter(
            AssemblyPoint.name == point_data["name"]
        ).first()

        if not existing:
            point = AssemblyPoint(**point_data)
            db.add(point)
            db.flush()
            points.append(point)
        else:
            points.append(existing)

    db.commit()
    print(f"✓ {len(points)} toplanma noktası oluşturuldu")
    return points


def create_demo_volunteers(db: Session, skills: list):
    """Demo gönüllüler oluştur"""
    volunteers_data = [
        {
            "tc_no": "12345678901",
            "first_name": "Ahmet",
            "last_name": "Yılmaz",
            "email": "ahmet.yilmaz@example.com",
            "phone": "0555 111 11 11",
            "password_hash": pwd_context.hash("123456"),
            "city": "Ankara",
            "district": "Çankaya",
            "latitude": 39.9334,
            "longitude": 32.8597,
            "birth_date": datetime(1990, 5, 15),
            "gender": "Erkek",
            "blood_type": BloodType.A_POSITIVE,
            "occupation": "Doktor",
            "education_level": "Üniversite",
            "status": VolunteerStatus.ACTIVE,
            "is_verified": True,
            "is_approved": True,
            "total_missions": 15,
            "completed_missions": 14,
            "total_hours": 120.5,
            "rating": 4.8,
            "skill_ids": [0, 8]  # İlk Yardım, Sağlık Personeli
        },
        {
            "tc_no": "12345678902",
            "first_name": "Ayşe",
            "last_name": "Demir",
            "email": "ayse.demir@example.com",
            "phone": "0555 222 22 22",
            "password_hash": pwd_context.hash("123456"),
            "city": "İstanbul",
            "district": "Kadıköy",
            "latitude": 40.9849,
            "longitude": 28.8594,
            "birth_date": datetime(1988, 8, 20),
            "gender": "Kadın",
            "blood_type": BloodType.O_NEGATIVE,
            "occupation": "Psikolog",
            "education_level": "Yüksek Lisans",
            "status": VolunteerStatus.ACTIVE,
            "is_verified": True,
            "is_approved": True,
            "total_missions": 10,
            "completed_missions": 10,
            "total_hours": 85.0,
            "rating": 5.0,
            "skill_ids": [2, 7]  # Psikososyal Destek, Çevirmenlik
        },
        {
            "tc_no": "12345678903",
            "first_name": "Mehmet",
            "last_name": "Kaya",
            "email": "mehmet.kaya@example.com",
            "phone": "0555 333 33 33",
            "password_hash": pwd_context.hash("123456"),
            "city": "Hatay",
            "district": "Antakya",
            "latitude": 36.2022,
            "longitude": 36.1604,
            "birth_date": datetime(1985, 3, 10),
            "gender": "Erkek",
            "blood_type": BloodType.B_POSITIVE,
            "occupation": "İtfaiyeci",
            "education_level": "Lise",
            "status": VolunteerStatus.ACTIVE,
            "is_verified": True,
            "is_approved": True,
            "total_missions": 25,
            "completed_missions": 23,
            "total_hours": 200.0,
            "rating": 4.9,
            "skill_ids": [1, 6]  # Arama-Kurtarma, Yangın Söndürme
        },
        {
            "tc_no": "12345678904",
            "first_name": "Fatma",
            "last_name": "Şahin",
            "email": "fatma.sahin@example.com",
            "phone": "0555 444 44 44",
            "password_hash": pwd_context.hash("123456"),
            "city": "Ankara",
            "district": "Keçiören",
            "latitude": 39.9700,
            "longitude": 32.8543,
            "birth_date": datetime(1992, 11, 25),
            "gender": "Kadın",
            "blood_type": BloodType.AB_POSITIVE,
            "occupation": "Aşçı",
            "education_level": "Meslek Lisesi",
            "status": VolunteerStatus.ACTIVE,
            "is_verified": True,
            "is_approved": True,
            "total_missions": 8,
            "completed_missions": 8,
            "total_hours": 60.0,
            "rating": 4.7,
            "skill_ids": [3, 9]  # Lojistik, Mutfak
        },
        {
            "tc_no": "12345678905",
            "first_name": "Can",
            "last_name": "Öztürk",
            "email": "can.ozturk@example.com",
            "phone": "0555 555 55 55",
            "password_hash": pwd_context.hash("123456"),
            "city": "İstanbul",
            "district": "Beşiktaş",
            "latitude": 41.0420,
            "longitude": 29.0088,
            "birth_date": datetime(1995, 7, 5),
            "gender": "Erkek",
            "blood_type": BloodType.A_NEGATIVE,
            "occupation": "Mühendis",
            "education_level": "Üniversite",
            "status": VolunteerStatus.ACTIVE,
            "is_verified": True,
            "is_approved": False,  # Onay bekliyor
            "total_missions": 0,
            "completed_missions": 0,
            "total_hours": 0.0,
            "rating": 5.0,
            "skill_ids": [4]  # İletişim
        }
    ]

    volunteers = []
    for vol_data in volunteers_data:
        existing = db.query(Volunteer).filter(
            Volunteer.email == vol_data["email"]
        ).first()

        if not existing:
            skill_ids = vol_data.pop("skill_ids", [])
            volunteer = Volunteer(**vol_data)
            db.add(volunteer)
            db.flush()

            # Yetkinlikleri ekle
            for skill_idx in skill_ids:
                if skill_idx < len(skills):
                    db.execute(
                        volunteer_skills.insert().values(
                            volunteer_id=volunteer.id,
                            skill_id=skills[skill_idx].id,
                            proficiency_level=4,  # 4/5 seviye
                            certified=True,
                            certificate_date=datetime.utcnow() - timedelta(days=365)
                        )
                    )

            volunteers.append(volunteer)
        else:
            volunteers.append(existing)

    db.commit()
    print(f"✓ {len(volunteers)} gönüllü oluşturuldu")
    return volunteers


def create_demo_disasters(db: Session):
    """Demo afetler oluştur"""
    disasters_data = [
        {
            "title": "Kahramanmaraş Depremi",
            "description": "7.8 büyüklüğünde deprem",
            "disaster_type": DisasterType.EARTHQUAKE,
            "severity": DisasterSeverity.CRITICAL,
            "status": DisasterStatus.ACTIVE,
            "location_name": "Kahramanmaraş Merkez",
            "city": "Kahramanmaraş",
            "district": "Dulkadiroğlu",
            "latitude": 37.5858,
            "longitude": 36.9350,
            "estimated_affected_people": 50000,
            "confirmed_deaths": 120,
            "confirmed_injured": 1500,
            "occurred_at": datetime.utcnow() - timedelta(hours=2),
            "reported_by_id": 1
        },
        {
            "title": "Hatay Sel Felaketi",
            "description": "Şiddetli yağış sonrası sel",
            "disaster_type": DisasterType.FLOOD,
            "severity": DisasterSeverity.HIGH,
            "status": DisasterStatus.ACTIVE,
            "location_name": "Hatay Antakya",
            "city": "Hatay",
            "district": "Antakya",
            "latitude": 36.2022,
            "longitude": 36.1604,
            "estimated_affected_people": 10000,
            "confirmed_deaths": 5,
            "confirmed_injured": 50,
            "occurred_at": datetime.utcnow() - timedelta(hours=6),
            "reported_by_id": 1
        }
    ]

    disasters = []
    for disaster_data in disasters_data:
        existing = db.query(Disaster).filter(
            Disaster.title == disaster_data["title"]
        ).first()

        if not existing:
            disaster = Disaster(**disaster_data)
            db.add(disaster)
            db.flush()
            disasters.append(disaster)
        else:
            disasters.append(existing)

    db.commit()
    print(f"✓ {len(disasters)} afet oluşturuldu")
    return disasters


def init_demo_data(db: Session):
    """Tüm demo verilerini oluştur"""
    print("\n🔧 Demo verileri oluşturuluyor...\n")

    # Sırasıyla oluştur
    skills = create_demo_skills(db)
    assembly_points = create_demo_assembly_points(db)
    volunteers = create_demo_volunteers(db, skills)
    disasters = create_demo_disasters(db)

    print("\n✅ Tüm demo verileri başarıyla oluşturuldu!\n")
    print("📋 Demo Gönüllü Girişleri:")
    print("   ahmet.yilmaz@example.com / 123456")
    print("   ayse.demir@example.com / 123456")
    print("   mehmet.kaya@example.com / 123456")
    print("   fatma.sahin@example.com / 123456")
    print("   can.ozturk@example.com / 123456 (Onay bekliyor)\n")
