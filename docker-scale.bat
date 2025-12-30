@echo off
REM ============================================================================
REM Scale Autom8 API Services
REM ============================================================================

echo.
echo ════════════════════════════════════════════════════════════════════════
echo   AUTOM8 SYSTEMS - Service Scaling
echo ════════════════════════════════════════════════════════════════════════
echo.

if "%1"=="" (
    echo Usage: docker-scale.bat [number]
    echo.
    echo Example: docker-scale.bat 3
    echo   This will run 3 instances of the API service
    echo.
    echo Current status:
    docker compose ps
    echo.
    pause
    exit /b 0
)

set SCALE_COUNT=%1

echo 📊 Current services:
docker compose ps
echo.

echo 🔄 Scaling API to %SCALE_COUNT% instances...
echo.

docker compose up -d --scale api=%SCALE_COUNT% --no-recreate

if errorlevel 1 (
    echo.
    echo ❌ Scaling failed
    echo.
    pause
    exit /b 1
)

echo.
echo ════════════════════════════════════════════════════════════════════════
echo   Scaling Complete!
echo ════════════════════════════════════════════════════════════════════════
echo.

REM Wait for services to stabilize
timeout /t 3 /nobreak >nul

echo 📊 New service status:
echo.
docker compose ps

echo.
echo ⚠  NOTE: When scaling, each instance needs unique ports
echo    or a load balancer in front. Current setup shares port 5000.
echo.
echo ════════════════════════════════════════════════════════════════════════
echo.

pause
