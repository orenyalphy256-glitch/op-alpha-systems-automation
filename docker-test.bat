@echo off
REM ============================================================================
REM Test Autom8 Docker Setup
REM ============================================================================

echo.
echo ════════════════════════════════════════════════════════════════════════
echo   AUTOM8 SYSTEMS - Docker Configuration Test
echo ════════════════════════════════════════════════════════════════════════
echo.

REM Test 1: Docker installation
echo [1/8] Testing Docker installation...
docker --version >nul 2>&1
if errorlevel 1 (
    echo     ❌ FAILED: Docker not installed
    goto :test_failed
) else (
    echo     ✅ PASSED: Docker is installed
)

REM Test 2: Docker running
echo [2/8] Testing Docker daemon...
docker info >nul 2>&1
if errorlevel 1 (
    echo     ❌ FAILED: Docker daemon not running
    goto :test_failed
) else (
    echo     ✅ PASSED: Docker daemon is running
)

REM Test 3: Docker Compose
echo [3/8] Testing Docker Compose...
docker compose version >nul 2>&1
if errorlevel 1 (
    echo     ❌ FAILED: Docker Compose not available
    goto :test_failed
) else (
    echo     ✅ PASSED: Docker Compose is available
)

REM Test 4: Compose file syntax
echo [4/8] Validating docker-compose.yml...
docker compose config >nul 2>&1
if errorlevel 1 (
    echo     ❌ FAILED: Invalid docker-compose.yml
    echo.
    echo     Running validation with output:
    docker compose config
    goto :test_failed
) else (
    echo     ✅ PASSED: docker-compose.yml is valid
)

REM Test 5: Environment file
echo [5/8] Checking environment file...
if exist .env (
    echo     ✅ PASSED: .env file exists
) else (
    echo     ⚠  WARNING: .env file not found
    echo     Using default values
)

REM Test 6: Dockerfile
echo [6/8] Checking Dockerfile...
if exist Dockerfile (
    echo     ✅ PASSED: Dockerfile exists
) else (
    echo     ❌ FAILED: Dockerfile not found
    goto :test_failed
)

REM Test 7: Build test
echo [7/8] Testing image build...
docker compose build >nul 2>&1
if errorlevel 1 (
    echo     ❌ FAILED: Image build failed
    goto :test_failed
) else (
    echo     ✅ PASSED: Image builds successfully
)

REM Test 8: Network configuration
echo [8/8] Testing network configuration...
docker network ls | findstr autom8 >nul 2>&1
if errorlevel 1 (
    echo     ℹ  INFO: Network will be created on first run
) else (
    echo     ✅ PASSED: Network exists
)

echo.
echo ════════════════════════════════════════════════════════════════════════
echo   ✅ ALL TESTS PASSED!
echo ════════════════════════════════════════════════════════════════════════
echo.
echo   Your Docker setup is ready!
echo.
echo   Next steps:
echo   1. Review .env configuration
echo   2. Run: docker-start.bat
echo   3. Test: docker-status.bat
echo.
echo ════════════════════════════════════════════════════════════════════════
echo.
pause
exit /b 0

:test_failed
echo.
echo ════════════════════════════════════════════════════════════════════════
echo   ❌ TESTS FAILED
echo ════════════════════════════════════════════════════════════════════════
echo.
echo   Please fix the errors above and run again.
echo.
echo ════════════════════════════════════════════════════════════════════════
echo.
pause
exit /b 1