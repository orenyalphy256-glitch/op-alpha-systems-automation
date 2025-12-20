# 🚀 Deployment Guide - Autom8

Production deployment guide for the Autom8 automation platform.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Configuration](#configuration)
4. [Deployment Methods](#deployment-methods)
5. [Database Setup](#database-setup)
6. [Security Hardening](#security-hardening)
7. [Monitoring](#monitoring)
8. [Backup & Recovery](#backup--recovery)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Minimum**:
- CPU: 2 cores
- RAM: 2GB
- Disk: 10GB
- OS: Linux (Ubuntu 20.04+), Windows Server 2019+

**Recommended**:
- CPU: 4 cores
- RAM: 4GB
- Disk: 20GB SSD
- OS: Ubuntu 22.04 LTS

### Software Requirements

- Python 3.11+
- Docker 20.10+ (for containerized deployment)
- PostgreSQL 13+ (production database)
- Nginx 1.18+ (reverse proxy)
- Git 2.30+

---

## Environment Setup

### 1. System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip \
  postgresql postgresql-contrib nginx git

# Install Docker (optional)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### 2. Create Application User

```bash
# Create dedicated user
sudo useradd -m -s /bin/bash autom8
sudo su - autom8
```

### 3. Clone Repository

```bash
cd /opt
sudo git clone https://github.com/orenyalphy256-glitch/op-alpha-systems-automation.git autom8
sudo chown -R autom8:autom8 /opt/autom8
cd /opt/autom8
```

---

## Configuration

### 1. Environment Variables

Create `.env` file:

```bash
cp .env.example .env
nano .env
```

**Production Configuration**:

```env
# Application
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=<generate-strong-secret-key>

# Database
DATABASE_URL=postgresql://autom8_user:strong_password@localhost:5432/autom8_db

# Security
JWT_SECRET_KEY=<generate-strong-jwt-secret>
ENCRYPTION_KEY=<generate-32-byte-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Rate Limiting
RATE_LIMIT_DEFAULT=200
RATE_LIMIT_OVERRIDE=5000

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/autom8/app.log

# Email (for alerts)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL=admin@yourdomain.com
```

### 2. Generate Secrets

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate ENCRYPTION_KEY
python generate_keys.py
```

---

## Deployment Methods

### Method 1: Docker Deployment (Recommended)

#### Single Container

```bash
# Build image
docker build -t autom8:1.0.0 .

# Run container
docker run -d \
  --name autom8 \
  -p 5000:5000 \
  -v /opt/autom8/data:/app/data \
  -v /opt/autom8/logs:/app/logs \
  --env-file .env \
  --restart unless-stopped \
  autom8:1.0.0
```

#### Docker Compose (Multi-Service)

```bash
# Start all services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale API instances
docker-compose up -d --scale api=3

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**docker-compose.prod.yml**:
```yaml
version: '3.8'

services:
  api:
    image: autom8:1.0.0
    environment:
      - FLASK_ENV=production
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
  
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: autom8_db
      POSTGRES_USER: autom8_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt
    depends_on:
      - api
    restart: always

volumes:
  postgres_data:
```

---

### Method 2: Systemd Service

#### 1. Create Service File

```bash
sudo nano /etc/systemd/system/autom8.service
```

```ini
[Unit]
Description=Autom8 API Service
After=network.target postgresql.service

[Service]
Type=simple
User=autom8
Group=autom8
WorkingDirectory=/opt/autom8
Environment="PATH=/opt/autom8/venv/bin"
EnvironmentFile=/opt/autom8/.env
ExecStart=/opt/autom8/venv/bin/python -m autom8.api
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 2. Enable and Start

```bash
sudo systemctl daemon-reload
sudo systemctl enable autom8
sudo systemctl start autom8
sudo systemctl status autom8
```

---

### Method 3: Gunicorn + Nginx

#### 1. Install Gunicorn

```bash
pip install gunicorn
```

#### 2. Create Gunicorn Config

```python
# gunicorn.conf.py
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
errorlog = "/var/log/autom8/gunicorn-error.log"
accesslog = "/var/log/autom8/gunicorn-access.log"
loglevel = "info"
```

#### 3. Run Gunicorn

```bash
gunicorn -c gunicorn.conf.py "autom8.api:create_app()"
```

---

## Database Setup

### PostgreSQL Configuration

#### 1. Create Database and User

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE autom8_db;
CREATE USER autom8_user WITH ENCRYPTED PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE autom8_db TO autom8_user;
\q
```

#### 2. Initialize Schema

```bash
python autom8/init_database.py
```

#### 3. Optimize PostgreSQL

Edit `/etc/postgresql/15/main/postgresql.conf`:

```conf
# Memory
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 16MB

# Connections
max_connections = 100

# Performance
random_page_cost = 1.1
effective_io_concurrency = 200
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

---

## Security Hardening

### 1. Firewall Configuration

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

### 2. SSL/TLS Setup (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### 3. Nginx Configuration

```nginx
# /etc/nginx/sites-available/autom8
upstream autom8_backend {
    server 127.0.0.1:5000;
    # Add more servers for load balancing
    # server 127.0.0.1:5001;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy Configuration
    location / {
        proxy_pass http://autom8_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files (if any)
    location /static {
        alias /opt/autom8/static;
        expires 30d;
    }

    # Logging
    access_log /var/log/nginx/autom8-access.log;
    error_log /var/log/nginx/autom8-error.log;
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/autom8 /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Monitoring

### 1. Application Monitoring

**Health Check Endpoint**:
```bash
curl https://yourdomain.com/api/v1/health
```

**Metrics Endpoint**:
```bash
curl https://yourdomain.com/api/v1/metrics
```

### 2. Log Monitoring

```bash
# Application logs
tail -f /var/log/autom8/app.log

# Nginx logs
tail -f /var/log/nginx/autom8-access.log
tail -f /var/log/nginx/autom8-error.log

# System logs
journalctl -u autom8 -f
```

### 3. Automated Monitoring

**Cron job for health checks**:
```bash
# Add to crontab
*/5 * * * * /opt/autom8/health-check.bat || mail -s "Autom8 Health Check Failed" admin@yourdomain.com
```

---

## Backup & Recovery

### 1. Database Backup

**Automated backup script**:
```bash
#!/bin/bash
# /opt/autom8/scripts/backup-db.sh

BACKUP_DIR="/opt/autom8/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/autom8_db_$DATE.sql.gz"

# Create backup
pg_dump -U autom8_user autom8_db | gzip > $BACKUP_FILE

# Keep only last 7 days
find $BACKUP_DIR -name "autom8_db_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
```

**Schedule backup**:
```bash
# Add to crontab
0 2 * * * /opt/autom8/scripts/backup-db.sh
```

### 2. Database Restore

```bash
# Restore from backup
gunzip < /opt/autom8/backups/autom8_db_20251220_020000.sql.gz | \
  psql -U autom8_user autom8_db
```

### 3. Application Backup

```bash
# Backup configuration and data
tar -czf autom8_backup_$(date +%Y%m%d).tar.gz \
  /opt/autom8/.env \
  /opt/autom8/data \
  /opt/autom8/logs
```

---

## Troubleshooting

### Common Issues

#### 1. Application Won't Start

**Check logs**:
```bash
journalctl -u autom8 -n 50
tail -f /var/log/autom8/app.log
```

**Common causes**:
- Missing environment variables
- Database connection failure
- Port already in use

#### 2. Database Connection Errors

**Test connection**:
```bash
psql -U autom8_user -d autom8_db -h localhost
```

**Check PostgreSQL status**:
```bash
sudo systemctl status postgresql
```

#### 3. High Memory Usage

**Check processes**:
```bash
ps aux | grep autom8
```

**Restart service**:
```bash
sudo systemctl restart autom8
```

#### 4. Slow Response Times

**Check database performance**:
```sql
SELECT * FROM pg_stat_activity;
```

**Clear cache**:
```bash
# Restart application to clear in-memory cache
sudo systemctl restart autom8
```

---

## Performance Tuning

### 1. Database Indexing

```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_contacts_created_at ON contacts(created_at);
```

### 2. Connection Pooling

Configure in `.env`:
```env
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

### 3. Caching

Enable Redis for distributed caching:
```bash
sudo apt install redis-server
sudo systemctl enable redis-server
```

Update `.env`:
```env
CACHE_TYPE=redis
CACHE_REDIS_URL=redis://localhost:6379/0
```

---

## Scaling

### Horizontal Scaling

1. **Load Balancer**: Use Nginx or HAProxy
2. **Multiple API Instances**: Scale with Docker Compose
3. **Shared Database**: PostgreSQL with read replicas
4. **Distributed Cache**: Redis cluster

### Vertical Scaling

1. **Increase resources**: CPU, RAM
2. **Optimize database**: Tune PostgreSQL settings
3. **Enable caching**: Reduce database load

---

## Rollback Procedure

### 1. Stop Current Version

```bash
docker-compose down
# or
sudo systemctl stop autom8
```

### 2. Restore Previous Version

```bash
git checkout <previous-tag>
docker-compose up -d
# or
sudo systemctl start autom8
```

### 3. Restore Database (if needed)

```bash
gunzip < backup.sql.gz | psql -U autom8_user autom8_db
```

---

## Deployment Checklist

See [DEPLOYMENT_CHECKLIST.md](../DEPLOYMENT_CHECKLIST.md) for complete pre-deployment verification.

---

*For additional support, contact: orenyalphy256@gmail.com*
