@echo off

REM ============================================================================

REM Run Tests in Watch Mode (Re-run on file changes)

REM ============================================================================



echo.

echo ════════════════════════════════════════════════════════════════════════

echo   AUTOM8 - Test Watch Mode

echo ════════════════════════════════════════════════════════════════════════

echo.

echo Tests will re-run automatically when files change.

echo Press Ctrl+C to stop.

echo.



call venv\\Scripts\\activate



REM Install pytest-watch if not installed

pip show pytest-watch >nul 2>\&1

if errorlevel 1 (

&nbsp;   echo Installing pytest-watch...

&nbsp;   pip install pytest-watch

)



echo 👀 Watching for changes...

echo.



pytest-watch -- -v --tb=short



pause
