@echo off
chcp 65001 >nul
echo ============================================================
echo 🚨 AFAD Gönüllü Yönetim Sistemi - Otomatik Kurulum
echo ============================================================
echo.

echo [1/5] Sanal ortam oluşturuluyor...
python -m venv venv
if errorlevel 1 (
    echo ❌ HATA: Python bulunamadı!
    echo Python 3.10+ yüklü olmalı: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [2/5] Sanal ortam aktif ediliyor...
call venv\Scripts\activate.bat

echo [3/5] Paketler yükleniyor... (Bu 1-2 dakika sürebilir)
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ❌ HATA: Paket yükleme başarısız!
    pause
    exit /b 1
)

echo [4/5] Veritabanı oluşturuluyor...
python run.py --init-db --demo
if errorlevel 1 (
    echo ❌ HATA: Veritabanı oluşturulamadı!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo ✅ KURULUM TAMAMLANDI!
echo ============================================================
echo.
echo 🎉 Sistem hazır! Sunucuyu başlatmak için:
echo    1. start_server.bat dosyasını çalıştırın
echo    VEYA
echo    2. Bu pencereyi kapatmayın, Enter'a basın
echo.
pause

echo.
echo [5/5] Sunucu başlatılıyor...
echo ============================================================
echo 📡 Backend: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo ============================================================
echo.
echo ⚠️  Sunucuyu durdurmak için: CTRL+C
echo.

python run.py --reload
