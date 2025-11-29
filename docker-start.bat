@echo off
REM Start all services

echo Starting Autom8 services...
docker compose up -d

echo.
echo Services started!
echo API: http://localhost:5000
echo.
echo View logs: docker compose logs -f
pause