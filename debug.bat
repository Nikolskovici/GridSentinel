@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0Interfata"

echo.
echo ========================================
echo GridSentinel DEBUG MODE
echo ========================================
echo.

echo [*] Starting Python server in new window...
start "GridSentinel Server" cmd /K "python -m uvicorn main:app --port 8000 --log-level debug 2>&1"

echo [*] Waiting 3 seconds for server to start...
timeout /t 3 /nobreak

echo [*] Starting Electron...
echo [*] Use Alt+D for DevTools, Alt+F4 to quit
echo.

npx electron . --enable-logging

echo.
echo [*] Debug session ended
pause
