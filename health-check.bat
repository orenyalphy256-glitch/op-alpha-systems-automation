@echo off
REM Autom8 Health Check Script
REM Performs comprehensive system health verification

echo ========================================
echo Autom8 Health Check
echo ========================================
echo.

set ERROR_COUNT=0

REM Check API Server
echo [1/7] Checking API server...
curl -s http://localhost:5000/api/v1/health >nul 2>&1
if errorlevel 1 (
    echo [FAIL] API server is not responding
    set /a ERROR_COUNT+=1
) else (
    echo [OK] API server is running
)
echo.

REM Check Database
echo [2/7] Checking database...
if exist data\autom8.db (
    echo [OK] Database file exists
) else (
    echo [FAIL] Database file not found
    set /a ERROR_COUNT+=1
)
echo.

REM Check Disk Space
echo [3/7] Checking disk space...
for /f "tokens=3" %%a in ('dir /-c ^| find "bytes free"') do set FREE_SPACE=%%a
echo [INFO] Free disk space: %FREE_SPACE% bytes
echo.

REM Check Log Files
echo [4/7] Checking log files...
if exist logs\app.log (
    for %%A in (logs\app.log) do set LOG_SIZE=%%~zA
    if %%~zA GTR 104857600 (
        echo [WARN] Log file is large (^>100MB): %%~zA bytes
    ) else (
        echo [OK] Log file size: %%~zA bytes
    )
) else (
    echo [WARN] Log file not found
)
echo.

REM Check Configuration
echo [5/7] Checking configuration...
if exist .env (
    echo [OK] Configuration file exists
) else (
    echo [FAIL] Configuration file (.env) not found
    set /a ERROR_COUNT+=1
)
echo.

REM Check Python Environment
echo [6/7] Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo [FAIL] Python not found
    set /a ERROR_COUNT+=1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo [OK] Python %%i
)
echo.

REM Check Dependencies
echo [7/7] Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [FAIL] Flask not installed
    set /a ERROR_COUNT+=1
) else (
    echo [OK] Flask is installed
)
echo.

REM Summary
echo ========================================
echo Health Check Summary
echo ========================================
if %ERROR_COUNT% EQU 0 (
    echo Status: ALL CHECKS PASSED
    echo System is healthy
    exit /b 0
) else (
    echo Status: %ERROR_COUNT% CHECK(S) FAILED
    echo System needs attention
    exit /b 1
)
