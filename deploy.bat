@echo off
REM Autom8 Deployment Script
REM Automated deployment with tests and verification

echo ========================================
echo Autom8 Deployment Script
echo ========================================
echo.

set ERROR_OCCURRED=0

REM Step 1: Run tests
echo [1/6] Running tests...
call run-tests.bat
if errorlevel 1 (
    echo ERROR: Tests failed. Deployment aborted.
    set ERROR_OCCURRED=1
    goto :end
)
echo Tests passed successfully
echo.

REM Step 2: Build Docker image
echo [2/6] Building Docker image...
docker build -t autom8:latest .
if errorlevel 1 (
    echo ERROR: Docker build failed
    set ERROR_OCCURRED=1
    goto :end
)
echo Docker image built successfully
echo.

REM Step 3: Tag with timestamp
echo [3/6] Tagging image...
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TAG=%datetime:~0,8%_%datetime:~8,6%
docker tag autom8:latest autom8:%TAG%
echo Tagged as autom8:%TAG%
echo.

REM Step 4: Stop existing containers
echo [4/6] Stopping existing containers...
docker-compose down
echo Containers stopped
echo.

REM Step 5: Deploy with docker-compose
echo [5/6] Deploying with docker-compose...
docker-compose up -d
if errorlevel 1 (
    echo ERROR: Deployment failed
    set ERROR_OCCURRED=1
    goto :end
)
echo Deployment started
echo.

REM Step 6: Wait and verify
echo [6/6] Verifying deployment...
timeout /t 10 /nobreak >nul
echo Waiting for services to start...

REM Check API health
curl -s http://localhost:5000/api/v1/health >nul 2>&1
if errorlevel 1 (
    echo WARNING: API health check failed
    echo Check logs: docker-compose logs -f
    set ERROR_OCCURRED=1
) else (
    echo API is responding
)
echo.

:end
echo ========================================
if %ERROR_OCCURRED% EQU 0 (
    echo Deployment Successful!
    echo ========================================
    echo.
    echo Services are running:
    docker-compose ps
    echo.
    echo View logs: docker-compose logs -f
    echo Stop services: docker-compose down
) else (
    echo Deployment Failed!
    echo ========================================
    echo.
    echo Please check the logs and fix any issues
    echo Rollback: docker-compose down
)
echo.
pause
exit /b %ERROR_OCCURRED%
