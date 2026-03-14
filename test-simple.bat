@echo off
cd /d "%~dp0Interfata"

echo.
echo ========================================
echo Testing Electron - SIMPLE VERSION
echo ========================================
echo.

echo [*] Make sure server is running on port 8000!
echo [*] If not, run test-server.bat in another terminal
echo.
echo [*] Starting Electron (simple version)...
echo.

npx electron electron-simple.js --enable-logging --verbose

pause
