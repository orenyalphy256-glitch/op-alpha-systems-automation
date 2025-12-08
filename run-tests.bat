@echo off

REM ============================================================================
REM Run All Tests with Coverage
REM ============================================================================

echo.
echo ════════════════════════════════════════════════════════════════════════
echo   AUTOM8 - Running Test Suite
echo ════════════════════════════════════════════════════════════════════════
echo.

REM Activate virtual environment
call venv\Scripts\activate

REM Run pytest with coverage
echo 🧪 Running tests with coverage...
echo.

pytest -v --cov=autom8 --cov-report=term-missing --cov-report=html --cov-report=xml

set TEST_EXIT_CODE=%ERRORLEVEL%

echo.
echo ════════════════════════════════════════════════════════════════════════
echo   Test Results
echo ════════════════════════════════════════════════════════════════════════
echo.

if %TEST_EXIT_CODE% equ 0 (
    echo ✅ All tests passed!
    echo.
    echo 📊 Coverage report generated:
    echo    - Terminal: See above
    echo    - HTML: htmlcov\index.html
    echo    - XML: coverage.xml
) else (
    echo ❌ Some tests failed!
    echo.
    echo Check output above for details.
)

echo.
echo ════════════════════════════════════════════════════════════════════════
echo.
echo Press any key to close this window...
pause >nul

exit /b %TEST_EXIT_CODE%