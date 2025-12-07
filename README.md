# 🆘 AFAD Gönüllü Yönetim Sistemi

Modern, kapsamlı bir afet gönüllü yönetim platformu. Afet durumlarında gönüllüleri akıllı algoritma ile eşleştiren, bildirim gönderen ve koordine eden tam özellikli bir sistem.

## 🎯 Ana Özellikler

### 🌟 Gönüllü Sistemi
- **Dışarıdan Kayıt**: Herkes gönüllü olarak kayıt olabilir
- **Profil Yönetimi**: Resim, yetkinlikler, acil durum iletişim
- **Yetkinlik Sistemi**: 10+ farklı yetkinlik kategorisi (İlk Yardım, Arama-Kurtarma, vb.)
- **Durum Takibi**: Aktif, Görevde, Müsait Değil durumları

### 🎯 Akıllı Eşleştirme Algoritması
Gönüllüleri afet çağrılarına otomatik eşleştirir:
- **%40** Yetkinlik Eşleşmesi
- **%30** Mesafe (Konum bazlı)
- **%20** Değerlendirme Puanı
- **%10** Deneyim

### 📢 Afet Çağrısı Yönetimi
- Afet başına birden fazla çağrı oluşturma
- Gerekli yetkinlikleri belirtme
- Öncelik seviyeleri (Düşük, Orta, Yüksek, Kritik)
- Otomatik/manuel gönüllü atama
- Toplu bildirim gönderme

### 🗺️ Harita & Konum
- **Google Maps entegrasyonu**
- Toplanma noktaları görüntüleme
- Gönüllü-afet arası mesafe hesaplama
- Gerçek zamanlı konum takibi

### 🔔 Bildirim Sistemi
- Afet çağrısı bildirimleri
- Gönüllü kabul/red sistemi
- Push notification desteği (altyapı hazır)

### 🚨 Acil Durum
- Tek tıkla 112 arama
- Acil durum iletişim bilgileri

## 🛠️ Teknoloji Yığını

**Backend:**
- Python 3.10+
- FastAPI (Modern web framework)
- SQLAlchemy ORM
- PostgreSQL/SQLite
- JWT Authentication
- Haversine mesafe hesaplama

**Frontend:**
- HTML5/CSS3/JavaScript
- Leaflet.js (OpenStreetMap)
- Responsive Design

## 🚀 Hızlı Başlangıç

### 1. Gereksinimler
```bash
Python 3.10+
pip
```

### 2. Backend Kurulumu

```bash
cd backend

# Sanal ortam oluştur
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Veritabanını oluştur ve demo verileri ekle
python run.py --init-db --demo

# Sunucuyu başlat
python run.py --reload
```

Backend: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

### 3. Frontend Kurulumu

```bash
cd frontend

# Basit HTTP sunucusu
python -m http.server 8080
# veya
npx serve public
```

Frontend: `http://localhost:8080`

## 👥 Demo Kullanıcılar

### Yönetici Paneli
```
Admin:       admin@afad.gov.tr / admin123
Koordinatör: koordinator@afad.gov.tr / koord123
```

### Gönüllü Girişi
```
ahmet.yilmaz@example.com  / 123456  (Doktor - Onaylı)
ayse.demir@example.com    / 123456  (Psikolog - Onaylı)
mehmet.kaya@example.com   / 123456  (İtfaiyeci - Onaylı)
fatma.sahin@example.com   / 123456  (Aşçı - Onaylı)
can.ozturk@example.com    / 123456  (Mühendis - Onay Bekliyor)
```

## 📱 Kullanım Kılavuzu

### Gönüllü Olarak Kayıt

1. `http://localhost:8080/volunteer-register.html` adresine gidin
2. Formu doldurun (TC, email, telefon, şehir vb.)
3. Kayıt olun
4. Yönetici onayını bekleyin
5. Onaylandıktan sonra `volunteer-login.html` ile giriş yapın

### Yönetici - Afet Çağrısı Oluşturma

1. Admin paneline giriş yapın
2. **Afet Çağrıları** menüsüne gidin
3. **Yeni Çağrı Oluştur**'a tıklayın
4. Afet seçin, detayları girin
5. **Akıllı Eşleştir** butonuna basın
6. Algoritma en uygun gönüllüleri bulacak
7. **Tümünü Ata ve Bildir** ile toplu atama yapın

### Gönüllü - Çağrıya Katılma

1. Gönüllü paneline giriş yapın
2. **Bekleyen Çağrılar** sekmesinde bildirimleri görün
3. Eşleşme skoru, mesafe ve detayları inceleyin
4. **Kabul Et** veya **Reddet** butonuna basın
5. Kabul ederseniz durumunuz "Görevde" olur

### Harita Kullanımı

1. Gönüllü panelinde **Harita** sekmesine gidin
2. Kendi konumunuz ve toplanma noktaları görünür
3. Toplanma noktalarına tıklayarak detayları görün

## 📊 API Endpoints

### Gönüllü API
- `POST /api/volunteers/register` - Kayıt ol
- `POST /api/volunteers/login` - Giriş yap
- `GET /api/volunteers/me` - Profilim
- `PUT /api/volunteers/me` - Profil güncelle
- `POST /api/volunteers/me/skills` - Yetkinlik ekle
- `GET /api/volunteers/` - Liste (admin)
- `POST /api/volunteers/{id}/approve` - Onayla (admin)

### Afet Çağrısı API
- `POST /api/disaster-calls/` - Yeni çağrı
- `GET /api/disaster-calls/` - Çağrıları listele
- `POST /api/disaster-calls/match` - Akıllı eşleştir
- `POST /api/disaster-calls/{id}/activate` - Aktif et
- `GET /api/disaster-calls/{id}/assignments` - Atananları gör
- `POST /api/disaster-calls/assignments/{id}/respond` - Kabul/Red

### Yetkinlikler & Toplanma Noktaları
- `GET /api/volunteers/skills/all` - Tüm yetkinlikler
- `GET /api/volunteers/assembly-points/` - Toplanma noktaları

Detaylı API dokümantasyonu: `http://localhost:8000/docs`

## 📁 Proje Yapısı

```
tayfori_1/
├── backend/
│   ├── app/
│   │   ├── models/           # Veritabanı modelleri
│   │   │   ├── volunteer.py  # Gönüllü, Yetkinlik, Toplanma Noktası
│   │   │   ├── disaster_call.py  # Afet Çağrısı, Atama, Bildirim
│   │   │   └── ...
│   │   ├── routes/           # API endpoints
│   │   │   ├── volunteers.py
│   │   │   ├── disaster_calls.py
│   │   │   └── ...
│   │   ├── services/         # İş mantığı
│   │   │   ├── volunteer_service.py
│   │   │   ├── disaster_call_service.py
│   │   │   └── matching_algorithm.py  # Akıllı eşleştirme
│   │   ├── schemas/          # Pydantic şemaları
│   │   └── utils/
│   │       └── init_demo_data.py  # Demo veri scripti
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   └── public/
│       ├── volunteer-register.html    # Gönüllü kayıt
│       ├── volunteer-login.html       # Gönüllü giriş
│       ├── volunteer-dashboard.html   # Gönüllü paneli
│       ├── volunteer-management.html  # Yönetici: Gönüllü yönetimi
│       └── disaster-call-management.html  # Yönetici: Çağrı yönetimi
└── README.md
```

## 🔐 Güvenlik

- JWT tabanlı kimlik doğrulama
- Şifre hash'leme (bcrypt)
- Rol bazlı erişim kontrolü
- Input validation (Pydantic)
- SQL injection koruması (ORM)

## 🌟 Öne Çıkan Özellikler

### 1. Akıllı Eşleştirme Algoritması
```python
# Mesafe hesaplama (Haversine)
distance = haversine(volunteer_lat, volunteer_lon, disaster_lat, disaster_lon)

# Toplam skor
score = (
    skill_match * 0.40 +
    distance_score * 0.30 +
    rating_score * 0.20 +
    experience_score * 0.10
) * 100
```

### 2. Yetkinlik Seviye Sistemi
- 1-5 arası yetkinlik seviyesi
- Sertifika durumu
- Sertifika tarihi

### 3. Otomatik Bildirim
- Afet çağrısı oluşturulduğunda
- Gönüllü atandığında
- Durum değişikliklerinde

## 🔧 Konfigürasyon

### Veritabanı
Varsayılan olarak SQLite kullanılır. PostgreSQL için:

```python
# backend/config.py
DATABASE_URL = "postgresql://user:pass@localhost/afad_db"
```

### Google Maps API
Frontend'de kendi API anahtarınızı kullanın:

```javascript
// OpenStreetMap yerine Google Maps
L.tileLayer('https://maps.googleapis.com/...')
```

## 📝 Geliştirme Notları

### Yeni Yetkinlik Ekleme
```python
skill = Skill(
    name="Yeni Yetkinlik",
    description="Açıklama",
    category="Kategori",
    icon="🎯",
    is_critical=False
)
db.add(skill)
db.commit()
```

### Eşleştirme Algoritmasını Özelleştirme
`backend/app/services/matching_algorithm.py` dosyasındaki ağırlıkları değiştirin:

```python
SKILL_WEIGHT = 0.40
DISTANCE_WEIGHT = 0.30
RATING_WEIGHT = 0.20
EXPERIENCE_WEIGHT = 0.10
```

## 🐛 Sorun Giderme

### Backend çalışmıyor
```bash
# Bağımlılıkları yeniden yükle
pip install -r requirements.txt

# Veritabanını sıfırla
rm database.db
python run.py --init-db --demo
```

### Frontend statik dosyalar yüklenmiyor
CORS hatası alıyorsanız, backend'de CORS ayarlarını kontrol edin.

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Push edin (`git push origin feature/AmazingFeature`)
5. Pull Request açın

## 📧 İletişim

Proje Sahibi: AFAD Teknoloji Ekibi

---

⭐ **Yıldız vermeyi unutmayın!**

## 📜 Lisans

MIT License
