@echo off
title QuantumCalc - Docker Test & Launch Suite
cd /d "%~dp0"

echo ======================================================================
echo    QUANTUMCALC DOCKER TESTING & DEPLOYMENT SUITE
echo ======================================================================
echo.

where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [!] Docker was not detected in PATH.
    echo     Please ensure Docker Desktop is installed and running on Windows.
    echo     Download: https://www.docker.com/products/docker-desktop/
    echo.
    echo In the meantime, you can test locally with:
    echo   - Backend tests : py -m unittest backend.test_api
    echo   - Full App      : py run_app.py
    echo.
    pause
    exit /b 1
)

echo [1/3] Building Docker images for backend & frontend...
docker compose build

if %ERRORLEVEL% NEQ 0 (
    echo [!] Docker build encountered an error.
    pause
    exit /b 1
)

echo.
echo [2/3] Starting containerized services in background...
docker compose up -d

echo.
echo [3/3] Running automated backend test suite inside container...
docker compose exec backend python -m unittest backend.test_api

echo.
echo ======================================================================
echo  [+] Services running in Docker:
echo      - Frontend UI  : http://localhost:3000
echo      - Backend API  : http://localhost:8000/docs
echo      - Health Check : http://localhost:8000/api/health
echo ======================================================================
echo  To stop containers: docker compose down
echo ======================================================================
pause
