@echo off
REM ============================================================================
REM Comprehensive Docker Compose Setup Test
REM ============================================================================

echo.
echo ════════════════════════════════════════════════════════════════════════
echo   AUTOM8 - Docker Compose Setup Verification
echo ════════════════════════════════════════════════════════════════════════
echo.

set TESTS_PASSED=0
set TESTS_FAILED=0

REM Test 1: Configuration validation
echo [TEST 1] Validating docker-compose.yml...
docker compose config >nul 2>&1
if errorlevel 1 (
    echo     ❌ FAILED
    set /a TESTS_FAILED+=1
) else (
    echo     ✅ PASSED
    set /a TESTS_PASSED+=1
)

REM Test 2: Build images
echo [TEST 2] Building images...
docker compose build >nul 2>&1
if errorlevel 1 (
    echo     ❌ FAILED
    set /a TESTS_FAILED+=1
) else (
    echo     ✅ PASSED
    set /a TESTS_PASSED+=1
)

REM Test 3: Start services
echo [TEST 3] Starting services...
docker compose up -d >nul 2>&1
if errorlevel 1 (
    echo     ❌ FAILED
    set /a TESTS_FAILED+=1
    goto :show_results
) else (
    echo     ✅ PASSED
    set /a TESTS_PASSED+=1
)

REM Test 4: Wait for services to initialize
echo [TEST 4] Waiting for services to initialize...
timeout /t 15 /nobreak >nul
docker compose ps | findstr "Up" >nul 2>&1
if errorlevel 1 (
    echo     ❌ FAILED
    set /a TESTS_FAILED+=1
) else (
    echo     ✅ PASSED
    set /a TESTS_PASSED+=1
)

REM Test 5: Health check
echo [TEST 5] Testing API health endpoint...
curl -s http://localhost:5000/api/v1/health >nul 2>&1
if errorlevel 1 (
    echo     ❌ FAILED
    set /a TESTS_FAILED+=1
) else (
    echo     ✅ PASSED
    set /a TESTS_PASSED+=1
)

REM Test 6: Check volumes
echo [TEST 6] Verifying volumes...
docker volume ls | findstr autom8_data >nul 2>&1
if errorlevel 1 (
    echo     ❌ FAILED
    set /a TESTS_FAILED+=1
) else (
    echo     ✅ PASSED
    set /a TESTS_PASSED+=1
)

REM Test 7: Check network
echo [TEST 7] Verifying network...
docker network ls | findstr autom8 >nul 2>&1
if errorlevel 1 (
    echo     ❌ FAILED
    set /a TESTS_FAILED+=1
) else (
    echo     ✅ PASSED
    set /a TESTS_PASSED+=1
)

REM Test 8: Service dependency
echo [TEST 8] Checking service dependencies...
docker compose ps | findstr "autom8_dashboard" | findstr "Up" >nul 2>&1
if errorlevel 1 (
    echo     ⚠  WARNING: Dashboard not running (may be expected)
) else (
    echo     ✅ PASSED
    set /a TESTS_PASSED+=1
)

:show_results
echo.
echo ════════════════════════════════════════════════════════════════════════
echo   Test Results
echo ════════════════════════════════════════════════════════════════════════
echo.
echo   Tests Passed: %TESTS_PASSED%
echo   Tests Failed: %TESTS_FAILED%
echo.

if %TESTS_FAILED% gtr 0 (
    echo   ❌ SOME TESTS FAILED
    echo.
    echo   Service status:
    docker compose ps
    echo.
    echo   Recent logs:
    docker compose logs --tail=20
) else (
    echo   ✅ ALL TESTS PASSED!
    echo.
    echo   Your Docker Compose setup is working perfectly!
)

echo.
echo ════════════════════════════════════════════════════════════════════════
echo.

REM Cleanup prompt
choice /C YN /M "Stop services now?"
if errorlevel 2 goto :keep_running
if errorlevel 1 goto :cleanup

:cleanup
echo.
echo Stopping services...
docker compose down
goto :end

:keep_running
echo.
echo Services still running. Stop with: docker-stop.bat
goto :end

:end
pause