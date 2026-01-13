# ⚡ Quick Start Guide - Autom8

Get up and running with Autom8 in 5 minutes!

## Prerequisites

- Python 3.11 or higher
- Git

## Installation

### Option 1: Automated Installation (Windows)

```bash
# Clone and install
git clone https://github.com/orenyalphy256-glitch/op-alpha-systems-automation.git
cd op-alpha-systems-automation
install.bat
```

The script will:
✅ Check Python version
✅ Create virtual environment
✅ Install dependencies
✅ Initialize database
✅ Generate encryption keys
✅ Create configuration file

### Option 2: Manual Installation

```bash
# 1. Clone repository
git clone https://github.com/orenyalphy256-glitch/op-alpha-systems-automation.git
cd op-alpha-systems-automation

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
copy .env.example .env

# 5. Initialize database
python autom8/init_database.py

# 6. Generate keys
python generate_keys.py
```

## Start the API

```bash
python -m autom8.api
```

**Output**:
```
 * Running on http://127.0.0.1:5000
 * Autom8 API v1.0.0 started successfully
```

## Your First API Call

### 1. Check Health

```bash
curl http://localhost:5000/api/v1/health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "Autom8 API",
  "version": "1.0.0",
  "environment": "development"
}
```

### 2. Create a Contact

```bash
curl -X POST http://localhost:5000/api/v1/contacts \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"John Doe\", \"phone\": \"0701234567\"}"
```

**Response**:
```json
{
  "id": 1,
  "name": "John Doe",
  "phone": "0701234567",
  "email": null,
  "created_at": "2026-01-14T10:00:00Z",
  "updated_at": "2026-01-14T10:00:00Z"
}
```

### 3. Get All Contacts

```bash
curl http://localhost:5000/api/v1/contacts
```

### 4. Get System Metrics

```bash
curl http://localhost:5000/api/v1/metrics
```

## Using Python

```python
import requests

BASE_URL = "http://localhost:5000/api/v1"

# Create contact
response = requests.post(
    f"{BASE_URL}/contacts",
    json={"name": "Jane Smith", "phone": "0702345678"}
)
contact = response.json()
print(f"Created contact ID: {contact['id']}")

# Get all contacts
response = requests.get(f"{BASE_URL}/contacts")
contacts = response.json()["contacts"]
for contact in contacts:
    print(f"{contact['name']}: {contact['phone']}")
```

## Using the CLI

```bash
# Check system health
autom8 health

# List contacts
autom8 contacts list

# Add contact (interactive)
autom8 contacts add

# Run tests
autom8 test
```

## Docker Quick Start

```bash
# Build and run
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Next Steps

1. **Explore the API**: See [API Documentation](API.md)
2. **Deploy to Production**: See [Deployment Guide](DEPLOYMENT.md)
3. **Understand Architecture**: See [Architecture Docs](ARCHITECTURE.md)
4. **Run Tests**: `pytest tests/ -v`
5. **Enable Scheduler**: `python run_scheduler.py`

## Common Issues

### Port Already in Use

```bash
# Change port in .env
PORT=5001
```

### Database Locked

```bash
# Delete and reinitialize
del data\autom8.db
python autom8/init_database.py
```

### Import Errors

```bash
# Install in development mode
pip install -e .
```

## Getting Help

- **Documentation**: [Full Docs](../README.md)
- **Issues**: [GitHub Issues](https://github.com/orenyalphy256-glitch/op-alpha-systems-automation/issues)
- **Email**: orenyalphy256@gmail.com

---

**You're all set!** 🎉 Start building with Autom8.
