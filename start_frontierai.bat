@echo off
title FrontierAI
cd /d "%~dp0"

echo.
echo ==========================================
echo              FRONTIERAI
echo ==========================================
echo.

echo [1/3] Checking Ollama...
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1

if errorlevel 1 (
    echo Ollama is not running.
    echo Starting Ollama...
    start "" "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" serve
    timeout /t 5 /nobreak >nul
)

echo Ollama OK
echo.

echo [2/3] Starting FrontierAI API...
start "FrontierAI API" cmd /k "cd /d ""%CD%"" && .venv\Scripts\python.exe -m uvicorn app.api.main:app --host 127.0.0.1 --port 8000"

echo Waiting for API...
timeout /t 5 /nobreak >nul

echo.
echo [3/3] Opening FrontierAI...
start "" "http://127.0.0.1:8000/"

echo.
echo ==========================================
echo        FRONTIERAI IS READY
echo ==========================================
echo.
pause