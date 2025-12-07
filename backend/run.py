#!/usr/bin/env python3
"""
AFAD Yönetim Sistemi - Ana Uygulama
"""
import argparse
import uvicorn
from app import create_app
from app.models.database import init_db, SessionLocal
from app.models.user import User, UserRole
from app.utils.security import get_password_hash
from config import settings


def initialize_database(with_demo=False):
    """Veritabanını başlat ve örnek veriler ekle"""
    print("🔧 Veritabanı başlatılıyor...")
    init_db()

    db = SessionLocal()
    try:
        # Admin kullanıcısı yoksa oluştur
        admin = db.query(User).filter(User.email == "admin@afad.gov.tr").first()
        if not admin:
            admin = User(
                email="admin@afad.gov.tr",
                username="admin",
                full_name="Sistem Yöneticisi",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True,
                phone="0555 000 00 01",
                department="Bilgi İşlem",
            )
            db.add(admin)
            print("✓ Admin kullanıcısı oluşturuldu")

        # Koordinatör kullanıcısı
        coordinator = (
            db.query(User).filter(User.email == "koordinator@afad.gov.tr").first()
        )
        if not coordinator:
            coordinator = User(
                email="koordinator@afad.gov.tr",
                username="koordinator",
                full_name="Afet Koordinatörü",
                hashed_password=get_password_hash("koord123"),
                role=UserRole.COORDINATOR,
                is_active=True,
                is_verified=True,
                phone="0555 000 00 02",
                department="Operasyon Merkezi",
            )
            db.add(coordinator)
            print("✓ Koordinatör kullanıcısı oluşturuldu")

        # Saha çalışanı
        field_worker = (
            db.query(User).filter(User.email == "saha@afad.gov.tr").first()
        )
        if not field_worker:
            field_worker = User(
                email="saha@afad.gov.tr",
                username="sahacalisan",
                full_name="Saha Çalışanı",
                hashed_password=get_password_hash("saha123"),
                role=UserRole.FIELD_WORKER,
                is_active=True,
                is_verified=True,
                phone="0555 000 00 03",
                department="Saha Operasyonları",
            )
            db.add(field_worker)
            print("✓ Saha çalışanı kullanıcısı oluşturuldu")

        # Gözlemci
        observer = db.query(User).filter(User.email == "gozlemci@afad.gov.tr").first()
        if not observer:
            observer = User(
                email="gozlemci@afad.gov.tr",
                username="gozlemci",
                full_name="Gözlemci",
                hashed_password=get_password_hash("gozlem123"),
                role=UserRole.OBSERVER,
                is_active=True,
                is_verified=True,
                phone="0555 000 00 04",
                department="İzleme Birimi",
            )
            db.add(observer)
            print("✓ Gözlemci kullanıcısı oluşturuldu")

        db.commit()
        print("\n✅ Veritabanı başarıyla başlatıldı!")
        print("\n📋 Varsayılan Kullanıcılar:")
        print("   Admin:       admin@afad.gov.tr / admin123")
        print("   Koordinatör: koordinator@afad.gov.tr / koord123")
        print("   Saha:        saha@afad.gov.tr / saha123")
        print("   Gözlemci:    gozlemci@afad.gov.tr / gozlem123")

        # Demo verileri ekle
        if with_demo:
            from app.utils.init_demo_data import init_demo_data
            init_demo_data(db)

    except Exception as e:
        print(f"❌ Hata: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description="AFAD Yönetim Sistemi")
    parser.add_argument(
        "--init-db", action="store_true", help="Veritabanını başlat"
    )
    parser.add_argument(
        "--demo", action="store_true", help="Demo verileri ekle (--init-db ile birlikte)"
    )
    parser.add_argument(
        "--host", type=str, default=settings.HOST, help="Sunucu host adresi"
    )
    parser.add_argument(
        "--port", type=int, default=settings.PORT, help="Sunucu port numarası"
    )
    parser.add_argument(
        "--reload", action="store_true", help="Auto-reload etkin (development)"
    )

    args = parser.parse_args()

    if args.init_db:
        initialize_database(with_demo=args.demo)
        return

    # FastAPI uygulamasını oluştur
    app = create_app()

    # Banner
    print("\n" + "=" * 60)
    print("🚨 AFAD YÖNETİM SİSTEMİ")
    print("=" * 60)
    print(f"📡 Sunucu: http://{args.host}:{args.port}")
    print(f"📚 API Docs: http://{args.host}:{args.port}/docs")
    print(f"🔄 Auto-reload: {'Aktif' if args.reload else 'Pasif'}")
    print("=" * 60 + "\n")

    # Sunucuyu başlat
    uvicorn.run(
        "app:create_app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        factory=True,
    )


if __name__ == "__main__":
    main()
