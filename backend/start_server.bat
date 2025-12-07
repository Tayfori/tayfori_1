@echo off
chcp 65001 >nul
echo ============================================================
echo 🚨 AFAD Backend Sunucusu Başlatılıyor...
echo ============================================================
echo.

if not exist "venv" (
    echo ❌ HATA: Önce SETUP.bat dosyasını çalıştırmalısınız!
    echo.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo ✅ Sunucu başlatıldı!
echo.
echo 📡 Backend: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo ⚠️  Sunucuyu durdurmak için: CTRL+C
echo ============================================================
echo.

python run.py --reload
