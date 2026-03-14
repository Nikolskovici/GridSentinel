@echo off
setlocal enabledelayedexpansion

echo [*] Test Electron startup
cd /d "%~dp0Interfata"
echo [*] Current dir: %cd%

REM Check if npm works
echo [*] Testing npm and electron...
call npm --version
call npx electron --version

echo [*] Starting Electron - you should see a window in 5-10 seconds
echo [!] If it fails, check the console output above for errors
call npx electron .

pause
