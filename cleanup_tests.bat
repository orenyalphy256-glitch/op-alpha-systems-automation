@echo off
REM ============================================================================
REM Cleanup Test Artifacts and Run Tests
REM ============================================================================

echo Cleaning up test artifacts...

REM Remove coverage files
if exist .coverage del /F /Q .coverage
if exist coverage.xml del /F /Q coverage.xml
if exist htmlcov rmdir /S /Q htmlcov

REM Remove pytest cache
if exist .pytest_cache rmdir /S /Q .pytest_cache
if exist tests\.pytest_cache rmdir /S /Q tests\.pytest_cache

REM Remove __pycache__
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

echo Cleanup complete!
echo.
echo Running tests...

call venv\Scripts\activate
pytest tests/ -v --cov=autom8 --cov-report=term-missing --cov-report=html

pause