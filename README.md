# 🚨 AFAD Yönetim Sistemi (Advanced Disaster Management System)

Modern, kapsamlı bir afet ve acil durum yönetim platformu.

## 🎯 Özellikler

### 📊 Ana Modüller
- **Dashboard**: Gerçek zamanlı afet durumu izleme ve istatistikler
- **Harita Sistemi**: İnteraktif afet bölgesi görselleştirme
- **Afetzede Yönetimi**: Kayıt, takip ve ihtiyaç analizi
- **Envanter Yönetimi**: Lojistik ve kaynak takibi
- **Bildirim Sistemi**: Gerçek zamanlı uyarılar ve koordinasyon
- **Raporlama**: Detaylı analiz ve dokümantasyon

### 🛠️ Teknoloji Yığını

**Backend:**
- Python 3.10+
- FastAPI (Modern, hızlı web framework)
- SQLAlchemy (ORM)
- PostgreSQL/SQLite
- JWT Authentication
- WebSocket desteği

**Frontend:**
- HTML5/CSS3/JavaScript (ES6+)
- Tailwind CSS
- Leaflet.js (OpenStreetMap)
- Chart.js
- Responsive Design

## 🚀 Kurulum

### Gereksinimler
- Python 3.10+
- Node.js 16+ (opsiyonel)
- PostgreSQL (veya SQLite)

### Backend Kurulumu

```bash
# Sanal ortam oluştur
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Veritabanını oluştur
python run.py --init-db

# Sunucuyu başlat
python run.py
```

### Frontend Kurulumu

```bash
cd frontend
# Basit HTTP sunucusu ile çalıştır
python -m http.server 8080
# veya
npx serve public
```

## 📖 Kullanım

1. Backend sunucusu: `http://localhost:8000`
2. Frontend arayüz: `http://localhost:8080`
3. API Dokümantasyonu: `http://localhost:8000/docs`

### Varsayılan Kullanıcılar

- **Admin**: admin@afad.gov.tr / admin123
- **Koordinatör**: koordinator@afad.gov.tr / koord123
- **Gözlemci**: gozlemci@afad.gov.tr / gozlem123

## 🔐 Güvenlik

- JWT tabanlı kimlik doğrulama
- Rol bazlı erişim kontrolü (RBAC)
- SQL injection koruması
- XSS koruması
- CORS yapılandırması

## 📁 Proje Yapısı

```
afad-system/
├── backend/              # Backend API
│   ├── app/
│   │   ├── models/      # Veritabanı modelleri
│   │   ├── routes/      # API endpoint'leri
│   │   ├── services/    # İş mantığı
│   │   └── utils/       # Yardımcı fonksiyonlar
│   ├── migrations/      # Veritabanı migrasyonları
│   └── tests/           # Unit testler
├── frontend/            # Frontend arayüz
│   ├── src/
│   │   ├── components/  # UI bileşenleri
│   │   ├── pages/       # Sayfalar
│   │   └── services/    # API servisleri
│   └── public/          # Statik dosyalar
├── database/            # Veritabanı dosyaları
├── docs/                # Dokümantasyon
└── config/              # Konfigürasyon dosyaları
```

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request açın

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 📧 İletişim

Proje Bakımcısı - AFAD Teknoloji Ekibi

---
⭐ Bu projeyi faydalı bulduysanız yıldız vermeyi unutmayın!
