@echo off
cd /d "%~dp0Interfata"

echo.
echo ========================================
echo Testing Electron Only
echo ========================================
echo.

echo [*] Make sure server is already running on port 8000!
echo [*] If not, run test-server.bat in another terminal first
echo.
echo [*] Starting Electron...
echo [*] Press Alt+D for DevTools
echo [*] Press Alt+F4 to quit
echo.

npx electron . --enable-logging --verbose

pause
