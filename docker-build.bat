@echo off
REM Build Docker image

echo Building autom8 Docker image...
docker build -t autom8:latest .

echo.
echo Build complete!
echo.
echo Run with: docker compose up -d
pause
