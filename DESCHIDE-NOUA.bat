@echo off
REM GridSentinel Launcher
REM Lanseaza aplicatia Electron + FastAPI

setlocal enabledelayedexpansion

cd /d "%~dp0Interfata" || (
  echo EROARE: Nu gasesc folder Interfata
  pause
  exit /b 1
)

REM Termin procesele vechi
taskkill /F /IM electron.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1

REM Asteapt putin
timeout /t 1 /nobreak >nul

echo.
echo ===============================
echo  GridSentinel - Deschidere
echo ===============================
echo Pornire Electron...
echo.

REM Lanseaza intr-un nou process
start "" /B node_modules\.bin\electron . >launch.log 2>&1

REM Asteapt putin sa porneasca
timeout /t 3 /nobreak >nul

REM Verifica daca s-a lansat
tasklist | findstr electron >nul
if %errorlevel% == 0 (
  echo [OK] Electron lansat cu succes
  echo.
  echo GridSentinel se deschide in cateva secunde...
  echo Pentru a inchid, inchideti fereastra Electron.
  echo.
) else (
  echo [EROARE] Electron nu a pornit
  echo Verifica fisierul launch.log pentru detalii
  echo.
  type launch.log
  pause
)

exit /b 0
