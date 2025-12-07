"""
AFAD Yönetim Sistemi - Konfigürasyon
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Uygulama ayarları"""

    # Uygulama
    APP_NAME: str = "AFAD Yönetim Sistemi"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Sunucu
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Veritabanı
    DATABASE_URL: str = "sqlite:///./database/afad.db"
    # PostgreSQL için: "postgresql://user:password@localhost/afad_db"

    # Güvenlik
    SECRET_KEY: str = "your-secret-key-change-this-in-production-afad2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 saat

    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:8080",
        "http://localhost:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:3000",
    ]

    # Dosya yükleme
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Email (opsiyonel)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # SMS (opsiyonel)
    SMS_API_KEY: Optional[str] = None
    SMS_API_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
