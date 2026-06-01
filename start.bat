@echo off
title Trinetra Enterprise SIEM
cls

echo.
echo  ========================================
echo      TRINETRA ENTERPRISE SIEM - Launcher
echo  ========================================
echo.

:: Check Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found. Install Python first.
    pause
    exit /b 1
)
echo [OK] Python found

:: Check Node
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js not found. Install Node.js first.
    pause
    exit /b 1
)
echo [OK] Node.js found

:: Check/Optional: Ollama
where ollama >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Ollama found
) else (
    echo [!] Ollama not found - AI features will show offline
)

:: Kill any existing on port 8000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr LISTENING') do (
    echo [*] Killing stale process on port 8000 (PID %%a)
    taskkill /F /PID %%a >nul 2>&1
)

:: Kill any existing on port 5173
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173" ^| findstr LISTENING') do (
    echo [*] Killing stale process on port 5173 (PID %%a)
    taskkill /F /PID %%a >nul 2>&1
)

:: Start Backend
echo.
echo [*] Starting Backend (port 8000)...
start "Trinetra-Backend" cmd /c "python run_backend.py & pause"

:: Wait for backend to initialize
timeout /t 4 /nobreak >nul

:: Check backend started
netstat -ano | findstr ":8000" | findstr LISTENING >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Backend running on http://localhost:8000
) else (
    echo [WARN] Backend may still be starting...
)

:: Start Frontend
echo.
echo [*] Starting Frontend (port 5173)...
cd /d "%~dp0frontend"
start "Trinetra-Frontend" cmd /c "npm run dev & pause"
cd /d "%~dp0"

:: Wait and check
timeout /t 5 /nobreak >nul

:: Open browser
echo.
echo  ========================================
echo     TRINETRA IS STARTING UP
echo  ========================================
echo.
echo     Frontend: http://localhost:5173
echo     Backend:  http://localhost:8000
echo     API Docs: http://localhost:8000/docs
echo     Health:   http://localhost:8000/health
echo.
echo     First time? Register at http://localhost:5173/register
echo.
echo     Close this window to stop all servers.
echo  ========================================
echo.

start http://localhost:5173

:: Keep this window open
echo Press any key to shut down all servers...
pause >nul

:: Cleanup
echo [*] Shutting down...
taskkill /F /FI "WINDOWTITLE eq Trinetra-Backend" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Trinetra-Frontend" >nul 2>&1
echo [OK] All servers stopped.
timeout /t 2 /nobreak >nul
