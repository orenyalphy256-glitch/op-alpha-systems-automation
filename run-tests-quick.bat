@echo off

REM ============================================================================

REM Run Tests Quickly (No Coverage, Stop on First Failure)

REM ============================================================================



echo.

echo ════════════════════════════════════════════════════════════════════════

echo   AUTOM8 - Quick Test Run

echo ════════════════════════════════════════════════════════════════════════

echo.



call venv\\Scripts\\activate



echo 🧪 Running tests (fast mode)...

echo.



REM Run only unit tests, stop on first failure

pytest tests/unit -v --maxfail=1 --tb=short



echo.

pause