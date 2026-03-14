@echo off
REM GridSentinel Desktop Application Launcher
REM Porneste serverul Python si aplicatia Electron

cd /d "%~dp0"

echo.
echo ===================================
echo GridSentinel Launcher
echo ===================================
echo.

REM Verific daca Python este disponibil
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Eroare: Python nu gasit in PATH
    echo Incerc sa gasesc Python 3.14...
    set "PYTHON_EXE=C:\Users\lakv6\AppData\Local\Programs\Python\Python314\python.exe"
    if not exist !PYTHON_EXE! (
        echo Eroare: Python 3.14 nu gasit
        pause
        exit /b 1
    )
) else (
    for /f %%i in ('where python') do set "PYTHON_EXE=%%i"
)

echo [*] Python: %PYTHON_EXE%

REM Verific daca serverul ruleaza deja
echo [*] Verific daca serverul e deja pornit...
netstat -ano | findstr :8000 >nul
if %ERRORLEVEL% EQU 0 (
    echo [+] Serverul ruleaza deja pe port 8000
) else (
    echo [*] Pornesc serverul Python...
    start "GridSentinel Server" cmd /K "cd /d "%~dp0Interfata" && %PYTHON_EXE% -m uvicorn main:app --port 8000"
    timeout /t 3 /nobreak
    echo [+] Serverul pornit in background
)

echo.
echo [*] Pornesc aplicatia Electron...
call npx electron .

echo.
echo Aplicatia s-a inchis.
pause
