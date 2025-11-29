@echo off
REM Stop all services

echo Stopping Autom8 services...
docker compose down

echo.
echo Services stopped!
pause