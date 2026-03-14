@echo off
REM GridSentinel - Just launch Electron app (assuming server is already running)

cd /d "%~dp0"

echo.
echo ===================================
echo GridSentinel App (Desktop Only)
echo ===================================
echo.
echo [*] Lansez aplicatia Electron...
echo [!] Asigura-te ca serverul Python ruleaza pe port 8000
echo.

call npx electron .

echo.
echo Aplicatia s-a inchis.
pause
