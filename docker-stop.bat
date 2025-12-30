@echo off
REM ============================================================================
REM Stop Autom8 Services
REM ============================================================================

echo.
echo ════════════════════════════════════════════════════════════════════════
echo   AUTOM8 SYSTEMS - Stopping Services
echo ════════════════════════════════════════════════════════════════════════
echo.

REM Show current status
echo 📊 Current Status:
echo.
docker compose ps

echo.
echo 🛑 Stopping services...
echo.

docker compose down

if errorlevel 1 (
    echo.
    echo ❌ Failed to stop services
    echo.
    pause
    exit /b 1
)

echo.
echo ════════════════════════════════════════════════════════════════════════
echo   Services Stopped Successfully!
echo ════════════════════════════════════════════════════════════════════════
echo.
echo   💾 Data volumes preserved
echo   📝 Logs preserved
echo.
echo   To start again: docker-start.bat
echo   To remove all data: docker compose down -v
echo.
echo ════════════════════════════════════════════════════════════════════════
echo.

pause
