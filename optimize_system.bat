@echo off
REM ============================================================================
REM System Optimization Quick Runner
REM ============================================================================

echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║           AUTOM8 - PERFORMANCE OPTIMIZATION SUITE                  ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

call venv\Scripts\activate

echo 1. Running performance examples...
python profile_examples.py

echo.
echo 2. Running performance tests...
pytest test_performance.py -v --tb=short
echo.
echo 3. Checking system health...
curl http://localhost:5000/api/v1/performance/health

echo.
echo 4. Getting performance stats...
curl http://localhost:5000/api/v1/performance/stats

echo.
echo ✅ Optimization suite complete!
echo.
echo 📊 Next steps:
echo    - Review profile results in profile_stats.txt
echo    - Check test output for performance issues
echo    - Monitor system metrics
echo.
pause
