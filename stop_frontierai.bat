@echo off
title Stop FrontierAI

echo.
echo ==========================================
echo        STOPPING FRONTIERAI
echo ==========================================
echo.

echo Stopping FrontierAI API...
taskkill /FI "WINDOWTITLE eq FrontierAI API*" /T /F >nul 2>&1

echo Stopping Ollama...
taskkill /IM ollama.exe /T /F >nul 2>&1

echo.
echo ==========================================
echo        FRONTIERAI STOPPED
echo ==========================================
echo.

pause