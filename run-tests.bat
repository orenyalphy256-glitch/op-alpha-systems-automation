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

call venv\\Scripts\\activate



REM Run pytest with coverage

echo 🧪 Running tests with coverage...

echo.



pytest -v --cov=autom8 --cov-report=term-missing --cov-report=html --cov-report=xml



set TEST\_EXIT\_CODE=%ERRORLEVEL%



echo.

echo ════════════════════════════════════════════════════════════════════════

echo   Test Results

echo ════════════════════════════════════════════════════════════════════════

echo.



if %TEST\_EXIT\_CODE% equ 0 (

&nbsp;   echo ✅ All tests passed!

&nbsp;   echo.

&nbsp;   echo 📊 Coverage report generated:

&nbsp;   echo    - Terminal: See above

&nbsp;   echo    - HTML: htmlcov\\index.html

&nbsp;   echo    - XML: coverage.xml

) else (

&nbsp;   echo ❌ Some tests failed!

&nbsp;   echo.

&nbsp;   echo Check output above for details.

)



echo.

echo ════════════════════════════════════════════════════════════════════════

echo.



pause

exit /b %TEST\_EXIT\_CODE%