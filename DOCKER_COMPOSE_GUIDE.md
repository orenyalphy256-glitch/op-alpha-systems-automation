markdown
# Docker Compose Guide - Autom8 Systems

Complete guide to multi-service orchestration for Autom8.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Service Details](#service-details)
4. [Configuration](#configuration)
5. [Commands Reference](#commands-reference)
6. [Scaling](#scaling)
7. [Troubleshooting](#troubleshooting)
8. [Production Deployment](#production-deployment)

## Quick Start

### First Time Setup

# 1. Test configuration
docker-test.bat

# 2. Start services
docker-start.bat

# 3. Check status
docker-status.bat

### Daily Usage

# Start
docker-start.bat

# View logs
docker-logs.bat

# Stop
docker-stop.bat

## Architecture Overview

### Service Architecture

┌─────────────────────────────────────────────────────────────┐
│                     Docker Host                              │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              autom8_network (bridge)                │    │
│  │                                                      │    │
│  │  ┌──────────────┐    ┌──────────────┐             │    │
│  │  │   API        │    │  Dashboard   │             │    │
│  │  │   Service    │◄───│   Service    │             │    │
│  │  │              │    │              │             │    │
│  │  │  Port: 5000  │    │  (Terminal)  │             │    │
│  │  └──────┬───────┘    └──────┬───────┘             │    │
│  │         │                   │                       │    │
│  │         └───────────┬───────┘                       │    │
│  │                     │                               │    │
│  │              ┌──────▼───────┐                       │    │
│  │              │   Volumes    │                       │    │
│  │              │              │                       │    │
│  │              │ autom8_data  │                       │    │
│  │              │ autom8_logs  │                       │    │
│  │              └──────────────┘                       │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘

### Data Flow

External Request (http://localhost:5000)
        ↓
Docker Port Mapping (5000:5000)
        ↓
autom8_network (Bridge Network)
        ↓
API Container (172.25.x.x:5000)
        ↓
Application Logic
        ↓
SQLite Database (autom8_data volume)
        ↓
Logs (autom8_logs volume)

## Service Details

### API Service

**Purpose:** Main application (Flask API + APScheduler)

**Configuration:**
- **Image:** autom8:latest
- **Port:** 5000 (configurable via API_PORT env var)
- **Resources:**
  - CPU Limit: 1.0 core
  - Memory Limit: 512MB
- **Health Check:** HTTP GET /api/v1/health every 30s
- **Restart Policy:** unless-stopped

**Volumes:**
- `/app/data` → autom8_data (database, uploads)
- `/app/logs` → autom8_logs (application logs)

**Dependencies:** None (runs first)

### Dashboard Service

**Purpose:** Real-time monitoring dashboard (terminal UI)

**Configuration:**
- **Image:** autom8:latest
- **Command:** `python -m autom8.dashboard`
- **Resources:**
  - CPU Limit: 0.5 core
  - Memory Limit: 256MB
- **Restart Policy:** unless-stopped

**Volumes:**
- `/app/data` → autom8_data (read-only)
- `/app/logs` → autom8_logs (read-only)

**Dependencies:**
- Waits for `api` service to be healthy

### DB-Init Service

**Purpose:** One-time database initialization

**Configuration:**
- **Image:** autom8:latest
- **Command:** `python -m autom8.init_database`
- **Restart Policy:** no (run once)

**Volumes:**
- `/app/data` → autom8_data (read-write)

## Configuration

### Environment Variables

**File:** `.env`

bash
# API Configuration
API_PORT=5000              # External port
API_HOST=0.0.0.0          # Bind address

# Application
APP_NAME=Autom8
ENVIRONMENT=development    # development | production

# Logging
LOG_LEVEL=INFO            # DEBUG | INFO | WARNING | ERROR
LOG_FORMAT=json           # json | text

# Scheduler
SCHEDULER_ENABLED=true
SCHEDULER_TIMEZONE=Africa/Nairobi

# Monitoring
METRICS_ENABLED=true
HEALTH_CHECK_ENABLED=true

# Alerts
ALERT_EMAIL=your@email.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

### Development vs Production

**Development (default):**

# Uses docker-compose.override.yml automatically
docker compose up -d

# Features:
 - Source code mounted (live reload)
 - Debug mode enabled
 - Verbose logging
 - Higher resource limits

**Production:**

# Explicitly use production config
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Features:
 - No source code mount
 - Debug mode disabled
 - Warning-level logging
 - Strict resource limits
 - Always restart policy

## Commands Reference

### Basic Operations

# Start services
docker compose up -d

# Stop services
docker compose down

# Restart services
docker compose restart

# View status
docker compose ps

# View logs (all services)
docker compose logs -f

# View logs (specific service)
docker compose logs -f api

### Building

# Build images
docker compose build

# Build without cache
docker compose build --no-cache

# Build and start
docker compose up -d --build

### Service Management

# Start specific service
docker compose start api

# Stop specific service
docker compose stop api

# Restart specific service
docker compose restart api

# Remove service container (keeps volumes)
docker compose rm api

### Inspection

# Show configuration
docker compose config

# Validate configuration
docker compose config --quiet

# Show images
docker compose images

# Show volumes
docker volume ls | findstr autom8

### Resource Monitoring

# Real-time resource usage
docker stats

# Service health
docker compose ps

# Detailed inspection
docker inspect autom8_api

## Scaling

### Horizontal Scaling

**Scale API service to 3 instances:**
docker compose up -d --scale api=3

**Result:**

autom8_api_1  (172.25.0.2:5000)
autom8_api_2  (172.25.0.3:5000)
autom8_api_3  (172.25.0.4:5000)

**Using helper script:**
docker-scale.bat 3

### Important Notes

⚠ **Port Conflict:** When scaling, all instances try to bind to port 5000!

**Solution 1: Random Ports**
yaml
# docker-compose.yml
services:
  api:
    ports:
      - "5000-5010:5000"  # Use range

**Solution 2: Load Balancer (Recommended)**
yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    depends_on:
      - api
  
  api:
    # No ports exposed (internal only)
    expose:
      - "5000"

**When to Scale:**

- High request volume
- CPU-intensive operations
- Need redundancy

**When NOT to Scale:**

- Database services
- Stateful services
- Services with scheduled jobs (creates duplicates!)

## Troubleshooting

### Service Won't Start

**Check logs:**
docker compose logs api

**Common causes:**
1. Port already in use
   # Find process using port
   netstat -ano | findstr :5000

   # Kill process
   taskkill /PID <pid> /F

2. Missing environment variables
   # Verify .env file exists
   type .env

3. Database locked
   # Stop all services
   docker compose down

   # Remove volumes and restart
   docker compose down -v
   docker compose up -d

### Container Exits Immediately

**Debug interactively:**

# Run container with shell
docker compose run --rm api bash

# Inside container, test manually
python run_combined.py

**Check health:**
docker inspect autom8_api | findstr Health

### Changes Not Reflected

**Rebuild images:**

# Stop services
docker compose down

# Rebuild without cache
docker compose build --no-cache

# Start fresh
docker compose up -d

**Or use helper:**
docker-rebuild.bat

### Network Issues

**Reset network:**

# Stop everything
docker compose down

# Remove network
docker network rm autom8_network

# Restart
docker compose up -d

**Test connectivity:**

# Enter API container
docker exec -it autom8_api bash

# Try to ping dashboard
ping autom8_dashboard

# Test DNS resolution
nslookup autom8_dashboard

### Volume Issues

**Check volume mounts:**
docker inspect autom8_api | findstr -A 5 Mounts

**Backup volume data:**

# Create backup
docker run --rm -v autom8_data:/data -v %cd%:/backup alpine tar czf /backup/data-backup.tar.gz /data

**Restore volume data:**

# Restore from backup
docker run --rm -v autom8_data:/data -v %cd%:/backup alpine tar xzf /backup/data-backup.tar.gz -C /

### Resource Exhaustion

**Check resource usage:**
docker stats --no-stream

**If memory limit reached:**
yaml

# Increase in docker-compose.yml

deploy:
  resources:
    limits:
      memory: 1G  # Increase from 512M

**If CPU throttling:**
yaml
deploy:
  resources:
    limits:
      cpus: '2.0'  # Increase from 1.0

## Production Deployment

### Pre-Deployment Checklist

- [ ] Update .env with production values
- [ ] Set DEBUG=false
- [ ] Configure SMTP credentials
- [ ] Set strong SECRET_KEY
- [ ] Review resource limits
- [ ] Enable proper logging
- [ ] Configure backups
- [ ] Set up monitoring
- [ ] Test health checks
- [ ] Configure SSL/TLS (if needed)

### Production Deployment

bash

# 1. Prepare environment
cp .env.example .env.prod

# Edit .env.prod with production values

# 2. Test configuration
docker compose -f docker-compose.yml -f docker-compose.prod.yml config

# 3. Deploy
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 4. Verify
docker compose ps
curl http://localhost:5000/api/v1/health

# 5. Monitor
docker compose logs -f

### Production Environment Variables

# .env.prod
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Use secure secrets
SECRET_KEY=<generate-secure-random-string>
API_KEY=<generate-secure-api-key>

# Production SMTP
SMTP_HOST=smtp.gmail.com
SMTP_USER=prod@company.com
SMTP_PASSWORD=<app-specific-password>

# Resource optimization
WORKERS=4
THREADS_PER_WORKER=2

### Backup Strategy

**Automated backup script:**
@echo off
REM backup-volumes.bat

set BACKUP_DIR=C:\Backups\autom8
set DATE=%date:-4,4%%date:-7,2%%date:~-10,2%

docker run --rm ^
  -v autom8_data:/data ^
  -v %BACKUP_DIR%:/backup ^
  alpine tar czf /backup/data-%DATE%.tar.gz /data

echo Backup complete: data-%DATE%.tar.gz

**Schedule with Task Scheduler:**

# Run daily at 2 AM
schtasks /create /tn "Autom8 Backup" /tr "C:\path\to\backup-volumes.bat" /sc daily /st 02:00

### Monitoring

**Health check endpoint:**

# Add to monitoring system (Nagios, Zabbix, etc.)
curl http://localhost:5000/api/v1/health

**Log aggregation:**
yaml

# Add to docker-compose.prod.yml
services:
  api:
    logging:
      driver: "syslog"
      options:
        syslog-address: "tcp://logs.company.com:514"

### Updates and Rollback

**Update to new version:**

# 1. Pull new code
git pull origin main

# 2. Rebuild
docker compose build

# 3. Rolling update (minimal downtime)
docker compose up -d --no-deps --build api

# 4. Verify
curl http://localhost:5000/api/v1/health

**Rollback:**

# 1. Stop current version
docker compose down

# 2. Checkout previous version
git checkout <previous-commit>

# 3. Rebuild and start
docker compose up -d --build

## 📊 Performance Tuning

### Optimize Image Size
dockerfile

# Use slim base images
FROM python:3.11-slim

# Combine RUN commands (fewer layers)
RUN apt-get update && \
    apt-get install -y gcc && \
    rm -rf /var/lib/apt/lists/*

# Use .dockerignore (already done!)

# Multi-stage builds (advanced)
FROM python:3.11 as builder

# Build dependencies
FROM python:3.11-slim

# Copy only what's needed

### Optimize Startup Time
yaml
services:
  api:
    # Skip unnecessary health check start period if app starts fast
    healthcheck:
      start_period: 10s  # Reduce from 40s if appropriate

### Resource Allocation

**Monitor and adjust:**

# Check actual usage
docker stats --no-stream

# If API uses 200MB consistently

# Adjust limits
deploy:
  resources:
    limits:
      memory: 300M  # Right-sized

## Best Practices

### DO ✅
- Use named volumes for persistent data
- Set resource limits
- Configure health checks
- Use environment variables for configuration
- Keep secrets in .env (not in code)
- Use specific image tags in production
- Monitor resource usage
- Implement proper logging
- Test compose configuration before deployment
- Use docker-compose.override.yml for local development

### DON'T ❌
- Hardcode secrets in docker-compose.yml
- Use `latest` tag in production
- Ignore health check failures
- Run containers as root (when avoidable)
- Mount sensitive host directories
- Forget to set restart policies
- Skip resource limits
- Use default networks in production
- Commit .env files to Git
- Scale stateful services without planning

### Official Documentation
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Compose File Reference](https://docs.docker.com/compose/compose-file/)
- [Docker Networks](https://docs.docker.com/network/)

### Autom8-Specific
- `debugging-cheat-sheet.md` - Docker debugging commands
- `README.md` - Project overview
- `.env.example` - Environment variable template
