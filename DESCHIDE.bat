@echo off
title GridSentinel — TRANSELECTRICA DSS
echo ========================================
echo   GridSentinel - Deschidere aplicatie
echo ========================================
echo.
echo [*] Verificare dependente...

cd /d "%~dp0Interfata" || (
  echo [!] Eroare: Nu gasesc folder Interfata
  pause
  exit /b 1
)

echo [OK] Folder: %cd%
echo.
echo [*] Pornire Electron + FastAPI...
echo     - Serverul va porni in background
echo     - Fereastra se va deschide in cateva secunde
echo.

npm start

echo.
echo [*] Inchidere...
timeout /t 2 >nul
exit /b 0
