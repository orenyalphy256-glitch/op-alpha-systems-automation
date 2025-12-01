@echo off
REM ============================================================================
REM Check Autom8 Services Status
REM ============================================================================

echo.
echo ════════════════════════════════════════════════════════════════════════
echo   AUTOM8 SYSTEMS - Service Status
echo ════════════════════════════════════════════════════════════════════════
echo.

REM Check Docker
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running
    echo.
    pause
    exit /b 1
)

REM Show service status
echo 📊 Services:
echo.
docker compose ps

echo.
echo ════════════════════════════════════════════════════════════════════════
echo   Resource Usage:
echo ════════════════════════════════════════════════════════════════════════
echo.
docker stats --no-stream

echo.
echo ════════════════════════════════════════════════════════════════════════
echo   Health Status:
echo ════════════════════════════════════════════════════════════════════════
echo.

REM Check API health
curl -s http://localhost:5000/api/v1/health 2>nul
if errorlevel 1 (
    echo ❌ API is not responding
) else (
    echo ✅ API is healthy
)

echo.
echo.
echo ════════════════════════════════════════════════════════════════════════
echo   Volume Information:
echo ════════════════════════════════════════════════════════════════════════
echo.
docker volume ls | findstr autom8

echo.
echo ════════════════════════════════════════════════════════════════════════
echo.

pause