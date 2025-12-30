@echo off
REM ============================================================================
REM Start Autom8 Services
REM ============================================================================

echo.
echo ════════════════════════════════════════════════════════════════════════
echo   AUTOM8 SYSTEMS - Starting Services
echo ════════════════════════════════════════════════════════════════════════
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running!
    echo.
    echo Please start Docker Desktop and try again.
    echo.
    pause
    exit /b 1
)

echo Docker is running
echo.

REM Check environment
if exist .env (
    echo Environment file found
) else (
    echo  WARNING: .env file not found
    echo    Using default values
)
echo.

REM Start services
echo Starting services...
echo.
docker compose up -d

if errorlevel 1 (
    echo.
    echo Failed to start services
    echo.
    pause
    exit /b 1
)

echo.
echo ════════════════════════════════════════════════════════════════════════
echo   Services Started Successfully!
echo ════════════════════════════════════════════════════════════════════════
echo.

REM Wait a moment for services to initialize
timeout /t 3 /nobreak >nul

REM Show status
echo Service Status:
echo.
docker compose ps

echo.
echo ════════════════════════════════════════════════════════════════════════
echo   Service URLs:
echo ════════════════════════════════════════════════════════════════════════
echo.
echo   🌐 API:          http://localhost:5000
echo   ❤  Health Check: http://localhost:5000/api/v1/health
echo   📊 Metrics:      http://localhost:5000/api/v1/metrics
echo.
echo ════════════════════════════════════════════════════════════════════════
echo   Useful Commands:
echo ════════════════════════════════════════════════════════════════════════
echo.
echo   View logs:       docker compose logs -f
echo   Stop services:   docker compose down
echo   Restart:         docker compose restart
echo   Status:          docker compose ps
echo.
echo ════════════════════════════════════════════════════════════════════════
echo.

pause
