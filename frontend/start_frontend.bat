@echo off
chcp 65001 >nul
echo ============================================================
echo 🌐 AFAD Frontend Sunucusu Başlatılıyor...
echo ============================================================
echo.

cd public

echo ✅ Frontend sunucusu başlatıldı!
echo.
echo 🌐 Ana Sayfa: http://localhost:8080/index.html
echo 👤 Gönüllü Kayıt: http://localhost:8080/volunteer-register.html
echo 🔑 Gönüllü Giriş: http://localhost:8080/volunteer-login.html
echo 🔧 Yönetici Giriş: http://localhost:8080/login.html
echo.
echo ⚠️  Sunucuyu durdurmak için: CTRL+C
echo ============================================================
echo.

python -m http.server 8080
