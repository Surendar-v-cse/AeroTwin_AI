@echo off
title AeroTwin AI Launcher
echo ========================================================
echo        AeroTwin AI - Localhost Startup Launcher
echo ========================================================
echo.

echo [1/2] Launching Backend (FastAPI / Uvicorn on port 8000)...
start "AeroTwin AI - Backend" cmd /k "python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Launching Frontend (Vite / React on port 5173)...
cd frontend
start "AeroTwin AI - Frontend" cmd /k "npm.cmd run dev"

echo.
echo ========================================================
echo Both services are now starting up in separate windows!
echo - Frontend Dashboard:  http://localhost:5173
echo - Backend API & Docs:   http://localhost:8000/docs
echo - Live WebSocket:       ws://127.0.0.1:8000/ws/telemetry
echo ========================================================
echo.
pause
