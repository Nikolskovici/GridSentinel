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
    echo [+] Serverul ruleaza pe port 8000
    REM Verific cu HTTP GET daca e responsive
    powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/status' -TimeoutSec 2 -ErrorAction Stop; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo [!] Server pe port 8000 nu raspunde - curatez procesul
        taskkill /F /IM python.exe >nul 2>nul
        timeout /t 1 /nobreak
    ) else (
        echo [+] Server conectat si responsive
        goto :startElectron
    )
)

echo [*] Pornesc serverul Python...
start "GridSentinel Server" cmd /K "cd /d "%~dp0Interfata" && %PYTHON_EXE% -m uvicorn main:app --reload --port 8000"
echo [*] Astept serverul sa se porneasca (max 10 secunde)...
for /L %%i in (1,1,20) do (
    timeout /t 0.5 /nobreak >nul 2>nul
    netstat -ano | findstr :8000 >nul
    if %ERRORLEVEL% EQU 0 (
        powershell -NoProfile -Command "try { Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/status' -TimeoutSec 1 -ErrorAction Stop | Out-Null; exit 0 } catch { exit 1 }" >nul 2>nul
        if %ERRORLEVEL% EQU 0 (
            echo [+] Server conectat cu succes
            goto :startElectron
        )
    )
)
echo [!] Avertisment: Serverul nu a raspuns in timp - incerc oricum sa pornesc Electron

:startElectron

echo.
echo [*] Pornesc aplicatia Electron...
cd /d "%~dp0Interfata"
call npx electron .

echo.
echo Aplicatia s-a inchis.
pause
