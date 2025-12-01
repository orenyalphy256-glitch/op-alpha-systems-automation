@echo off
REM ============================================================================
REM Rebuild and Restart Autom8 Services
REM ============================================================================

echo.
echo ════════════════════════════════════════════════════════════════════════
echo   AUTOM8 SYSTEMS - Rebuild Services
echo ════════════════════════════════════════════════════════════════════════
echo.

echo 🛑 Stopping current services...
docker compose down

echo.
echo 🔨 Rebuilding images...
echo.
docker compose build --no-cache

if errorlevel 1 (
    echo.
    echo ❌ Build failed
    echo.
    pause
    exit /b 1
)

echo.
echo 🚀 Starting rebuilt services...
echo.
docker compose up -d

if errorlevel 1 (
    echo.
    echo ❌ Failed to start
    echo.
    pause
    exit /b 1
)

echo.
echo ════════════════════════════════════════════════════════════════════════
echo   Rebuild Complete!
echo ════════════════════════════════════════════════════════════════════════
echo.

REM Show status
docker compose ps

echo.
pause