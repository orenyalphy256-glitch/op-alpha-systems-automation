@echo off
REM Quick Pipeline Run (Lint + Test only)
REM

echo.
echo AUTOM8: Quick Pipeline Run (Lint + Test only)
echo ----------------------------------------------------------------

call venv\Scripts\activate

echo Running Linting...
flake8 autom8/ --count

echo.
echo Running Tests...
pytest tests/ -v --tb=short

echo.
echo AUTOM8: Quick Pipeline Run Completed
pause