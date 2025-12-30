@echo off
REM Run Complete CI/CD Pipeline
REM

echo.
echo Starting CI/CD Pipeline...
echo.

REM Activate virtual environment
call venv\Scripts\activate

REM Run Pipeline
python ci_pipeline.py

set PIPELINE_EXIT_CODE=%ERRORLEVEL%

echo.
if %PIPELINE_EXIT_CODE% EQU 0 (
    echo CI/CD Pipeline completed successfully.
) else (
    echo CI/CD Pipeline failed with exit code %PIPELINE_EXIT_CODE%.
)

echo.
pause
exit /b %PIPELINE_EXIT_CODE%
