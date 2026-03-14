@echo off
setlocal enabledelayedexpansion

echo [*] Test server startup
cd /d "%~dp0Interfata"
echo [*] Current dir: %cd%

REM Find Python
for /f %%i in ('where python') do set "PYTHON_EXE=%%i"
echo [*] Python: !PYTHON_EXE!

if "!PYTHON_EXE!"=="" (
    echo [!] Python not found!
    pause
    exit /b 1
)

echo [*] Starting uvicorn...
!PYTHON_EXE! -m uvicorn main:app --port 8000 --log-level info

pause
