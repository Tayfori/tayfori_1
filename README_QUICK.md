# 🆘 AFAD Gönüllü Yönetim Sistemi

## ⚡ HIZLI BAŞLANGIÇ (3 Adım)

### 1️⃣ Gereksinim: Python Kurulu Olmalı

**Python var mı kontrol edin:**
```powershell
python --version
```

Eğer hata alırsanız → Python indirin: https://www.python.org/downloads/
- ✅ **"Add Python to PATH"** seçeneğini işaretleyin!

---

### 2️⃣ Backend Kurulum (TEK TIK!)

```
📂 backend klasörüne gidin
🖱️ SETUP.bat dosyasına ÇİFT TIK yapın
⏳ Bekleyin (1-2 dakika)
✅ "Kurulum tamamlandı" mesajını görün
```

**Otomatik yapılacaklar:**
- Sanal ortam oluşturma
- Paketleri yükleme
- Veritabanı + demo verileri
- Sunucuyu başlatma

---

### 3️⃣ Frontend Başlatma (TEK TIK!)

**Yeni bir klasör penceresi açın:**

```
📂 frontend klasörüne gidin
🖱️ start_frontend.bat dosyasına ÇİFT TIK yapın
✅ Tarayıcıda açılacak!
```

---

## 🌐 Sistem Adresleri

**Backend (API):** http://localhost:8000/docs
**Frontend (Ana Sayfa):** http://localhost:8080/index.html
**Gönüllü Kayıt:** http://localhost:8080/volunteer-register.html
**Gönüllü Giriş:** http://localhost:8080/volunteer-login.html
**Yönetici Girişi:** http://localhost:8080/login.html

---

## 👥 Demo Hesaplar

### Yönetici
```
Email: admin@afad.gov.tr
Şifre: admin123
```

### Gönüllüler (Onaylı)
```
ahmet.yilmaz@example.com / 123456 (Doktor)
ayse.demir@example.com / 123456 (Psikolog)
mehmet.kaya@example.com / 123456 (İtfaiyeci)
fatma.sahin@example.com / 123456 (Aşçı)
```

### Onay Bekleyen
```
can.ozturk@example.com / 123456 (Mühendis)
```

---

## ⚠️ Sorun Giderme

### "Python bulunamadı" hatası
→ Python kurun: https://www.python.org/downloads/
→ Kurulumda **"Add Python to PATH"** seçeneğini işaretleyin

### Port 8000 kullanımda
→ Başka bir uygulama 8000 portunu kullanıyor
→ O uygulamayı kapatın veya bilgisayarı yeniden başlatın

### Paketler yüklenmiyor
→ İnternet bağlantınızı kontrol edin
→ `pip install --upgrade pip` komutunu çalıştırın

### Veritabanı hatası
→ `backend/database.db` dosyasını silin
→ `SETUP.bat`'ı tekrar çalıştırın

---

## 🔄 Sonraki Kullanımlar

**Backend'i başlatmak için:**
```
backend/start_server.bat (çift tık)
```

**Frontend'i başlatmak için:**
```
frontend/start_frontend.bat (çift tık)
```

---

## 📁 Proje Yapısı

```
tayfori_1/
├── backend/
│   ├── SETUP.bat           ← İLK KURULUM (bir kez)
│   ├── start_server.bat    ← Sunucu başlat
│   └── ...
├── frontend/
│   ├── start_frontend.bat  ← Frontend başlat
│   └── public/
│       ├── volunteer-register.html
│       ├── volunteer-login.html
│       └── ...
└── README_QUICK.md (bu dosya)
```

---

## 🎯 Özellikler

✅ **Gönüllü Kayıt Sistemi** - Herkes kayıt olabilir
✅ **Akıllı Eşleştirme** - Yetkinlik, mesafe, deneyim bazlı
✅ **Google Maps Entegrasyonu** - Toplanma noktaları
✅ **Bildirim Sistemi** - Afet çağrıları
✅ **Yönetici Paneli** - Gönüllü onaylama, çağrı oluşturma
✅ **112 Acil Arama** - Tek tıkla acil durum

---

## 💬 Destek

**GitHub:** https://github.com/Tayfori/tayfori_1
**Branch:** claude/disaster-volunteer-system-018cVqDKYQUtjtd6KqTBJyhB

---

⭐ Projeyi beğendiyseniz GitHub'da yıldız verin!
