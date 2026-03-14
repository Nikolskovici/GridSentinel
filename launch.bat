@echo off
setlocal enabledelayedexpansion
REM GridSentinel Desktop Application Launcher
REM Porneste serverul Python si aplicatia Electron

cd /d "%~dp0"

echo.
echo ===================================
echo GridSentinel Launcher
echo ===================================
echo.

REM Verific daca Python este disponibil
echo [*] Cauta Python in PATH...

REM Incearca sa gaseasca Python direct din locatiile standard
set "PYTHON_PATHS=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python314\python.exe;C:\Python314\python.exe;C:\Program Files\Python314\python.exe"

set "PYTHON_EXE="
for %%p in (%PYTHON_PATHS%) do (
    if not defined PYTHON_EXE (
        if exist "%%p" (
            set "PYTHON_EXE=%%p"
            echo [✓] Python gasit la: %%p
        )
    )
)

REM Daca nu a gasit, incearca 'where' dar ignora shimul Windows Store
if not defined PYTHON_EXE (
    for /f %%i in ('where python 2^>nul') do (
        echo [*] Verificare: %%i
        if not "%%i"=="C:\Users\%USERNAME%\AppData\Local\Microsoft\WindowsApps\python.exe" (
            set "PYTHON_EXE=%%i"
        )
    )
)

if not defined PYTHON_EXE (
    echo [!] Eroare: Python 3.14 nu gasit. Asigura-te ca e instalat!
    echo [*] Asteptam input...
    pause
    exit /b 1
)

REM Verifica daca executable-ul exista cu adevarat
if not exist "!PYTHON_EXE!" (
    echo [!] Eroare: Python executable nu exista la !PYTHON_EXE!
    pause
    exit /b 1
)

echo [✓] Python: !PYTHON_EXE!

echo.
echo [*] Verific daca serverul e deja pornit...
netstat -ano 2>nul | findstr :8000 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [✓] Serverul ruleaza pe port 8000
    REM Verific cu HTTP GET daca e responsive - fara security warning
    powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/status' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo [✓] Server conectat si responsive
        goto :startElectron
    ) else (
        echo [!] Server pe port 8000 nu raspunde - curatez...
        taskkill /F /IM python.exe >nul 2>nul
        timeout /t 2 /nobreak >nul
    )
)

echo [*] Pornesc serverul Python in background...
set "SERVER_DIR=%CD%\Interfata"
echo [*] Directorul serverului: !SERVER_DIR!

REM Verific daca directorul exista
if not exist "!SERVER_DIR!" (
    echo [!] Eroare: Directorul !SERVER_DIR! nu exista!
    pause
    exit /b 1
)

REM Porneste serverul Python cu window vizibil pentru debugging
start "GridSentinel Python Server" /D "!SERVER_DIR!" "!PYTHON_EXE!" -m uvicorn main:app --port 8000

echo [*] Astept serverul sa se porneasca...
set "TIMEOUT_COUNT=0"
:waitServer
set /a "TIMEOUT_COUNT=!TIMEOUT_COUNT!+1"
if !TIMEOUT_COUNT! gtr 60 (
    echo [!] Timeout: Serverul nu a raspuns in 30 secunde
    goto :startElectronAnyway
)

timeout /t 0.5 /nobreak >nul 2>nul
netstat -ano 2>nul | findstr :8000 >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    goto :waitServer
)

REM Verific daca e responsive
powershell -NoProfile -Command "try { Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/status' -TimeoutSec 1 -UseBasicParsing -ErrorAction Stop | Out-Null; exit 0 } catch { exit 1 }" 2>nul
if %ERRORLEVEL% NEQ 0 (
    goto :waitServer
)

echo [✓] Server conectat cu succes pe port 8000
goto :startElectron

:startElectronAnyway
echo [!] Avertisment: Incerc sa pornesc Electron oricum...

:startElectron

echo.
echo [*] Pornesc aplicatia Electron...
cd /d "%~dp0Interfata"
call npx electron .

echo.
echo Aplicatia s-a inchis.
pause
