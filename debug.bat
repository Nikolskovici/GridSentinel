@echo off
REM Debug launcher - displays both server and electron logs

cd /d "%~dp0Interfata"

echo.
echo ╔════════════════════════════════════════╗
echo ║  GridSentinel DEBUG MODE               ║
echo ╚════════════════════════════════════════╝
echo.

echo [*] Starting Python server in new window...
start "GridSentinel Server" cmd /K "python -m uvicorn main:app --port 8000 --log-level debug"

echo [*] Waiting 3 seconds for server to start...
timeout /t 3 /nobreak

echo [*] Starting Electron with debugging...
echo [*] Press Alt+D to toggle DevTools if app opens
echo.

npx electron . --enable-logging

echo.
echo [*] Debug session ended
pause
