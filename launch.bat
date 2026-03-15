@echo off
REM GridSentinel Desktop Application Launcher — MODIFICAT
REM Porneste serverul Python si aplicatia Electron

cd /d "%~dp0"
echo Current dir: %cd%

echo.
echo ===================================
echo GridSentinel Launcher - REPAIR MODE
echo ===================================
echo.

REM Pasul 1: Curatare procese blocate (evita eroarea de Port 8000 ocupat)
echo [] Inchid procese vechi pentru a evita conflictele...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1

echo.
REM Pasul 2: Pornire Server
echo [] Pornesc serverul Python (Inima GridSentinel)...
REM Folosim "python main.py" pentru ca am pus uvicorn.run inauntru
start "GridSentinel Server" cmd /K "python main.py"

echo.
REM Pasul 3: Asteptare (Marim la 6 secunde pentru siguranta)
echo [] Astept 6 secunde sa se incarce modulele AI si Serverul...
timeout /t 6 /nobreak

echo.
REM Pasul 4: Pornire Electron
echo [] Pornesc aplicatia Electron...
cd /d "%~dp0.."
call npx electron .

echo.
echo [+] Aplicatia s-a inchis.
pause