@echo off
cd /d "%~dp0Interfata"

echo.
echo ========================================
echo Testing Python Server Only
echo ========================================
echo.

echo [*] Starting uvicorn on port 8000...
echo [*] Go to http://127.0.0.1:8000/api/status in browser
echo [*] Press CTRL+C to stop
echo.

python -m uvicorn main:app --port 8000 --log-level debug --reload

pause
