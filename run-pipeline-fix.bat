@echo off
REM Auto-fix Code Quality Issues in CI/CD Pipeline
REM

echo.
echo AUTOM8 - AUTO-FIX CODE QUALITY ISSUES
echo.

call venv\Scripts\activate

echo Running black code formatter...
black autom8/

echo.
echo Sorting imports with isort...
pip install isort
isort autom8/ --profile black

echo.
echo Code quality issues fixed successfully!
echo Run tests to verify: run-test.bat
pause