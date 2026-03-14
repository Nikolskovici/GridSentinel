@echo off
REM GridSentinel Desktop Application Launcher
REM Porneste serverul Python si aplicatia Electron

cd /d "%~dp0.."
echo Current dir: %cd%

echo.
echo ===================================
echo GridSentinel Launcher
echo ===================================
echo.

REM Verific daca serverul ruleaza deja
echo [*] Verific daca serverul e deja pornit...
netstat -ano | findstr :8000 >nul
if %ERRORLEVEL% EQU 0 (
    echo [+] Serverul ruleaza deja pe port 8000
) else (
    echo [*] Pornesc serverul Python in background...
    start "GridSentinel Server" cmd /K "cd /d "%~dp0" && python -m uvicorn main:app --port 8000"
    timeout /t 3 /nobreak
    echo [+] Serverul pornit
)

echo.
echo [*] Pornesc aplicatia Electron...
call npx electron .

echo.
echo Aplicatia s-a inchis.
pause

