@echo off
REM GridSentinel - Start Backend Server Only

cd /d "%~dp0Interfata"

echo.
echo ===================================
echo GridSentinel Backend Server
echo ===================================
echo.

set "PYTHON_EXE=C:\Users\lakv6\AppData\Local\Programs\Python\Python314\python.exe"

if not exist "%PYTHON_EXE%" (
    echo Eroare: Python nu gasit la %PYTHON_EXE%
    echo Incerc sa gasesc Python in PATH...
    for /f %%i in ('where python') do set "PYTHON_EXE=%%i"
)

echo [*] Python: %PYTHON_EXE%
echo [*] Pornesc serverul FastAPI pe port 8000...
echo [*] Serverul va rula pana inchizi aceasta fereastra
echo.

"%PYTHON_EXE%" -m uvicorn main:app --port 8000 --reload

echo.
echo Serverul s-a oprit.
pause
