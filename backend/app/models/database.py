"""
Veritabanı bağlantısı ve oturum yönetimi
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config import settings
import os

# Veritabanı dizinini oluştur
os.makedirs("./database", exist_ok=True)

# SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG,
)

# Session oluşturucu
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base model
Base = declarative_base()


def get_db():
    """Veritabanı oturumu dependency'si"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Veritabanını başlat ve tabloları oluştur"""
    # Tüm modelleri import et
    from backend.app.models import user, disaster, victim, inventory, notification

    # Tabloları oluştur
    Base.metadata.create_all(bind=engine)
    print("✓ Veritabanı tabloları oluşturuldu")
