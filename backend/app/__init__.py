"""
AFAD Yönetim Sistemi - Ana Uygulama Modülü
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import settings
import os


def create_app() -> FastAPI:
    """FastAPI uygulamasını oluştur ve yapılandır"""

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Modern Afet ve Acil Durum Yönetim Platformu",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Upload dizinini oluştur
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Route'ları import et ve kaydet
    from app.routes import (
        auth,
        users,
        disasters,
        victims,
        inventory,
        notifications,
        dashboard,
    )

    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(users.router, prefix="/api/users", tags=["Users"])
    app.include_router(disasters.router, prefix="/api/disasters", tags=["Disasters"])
    app.include_router(victims.router, prefix="/api/victims", tags=["Victims"])
    app.include_router(inventory.router, prefix="/api/inventory", tags=["Inventory"])
    app.include_router(
        notifications.router, prefix="/api/notifications", tags=["Notifications"]
    )
    app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

    @app.get("/")
    async def root():
        return {
            "message": "AFAD Yönetim Sistemi API",
            "version": settings.APP_VERSION,
            "docs": "/docs",
        }

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "app": settings.APP_NAME}

    return app
