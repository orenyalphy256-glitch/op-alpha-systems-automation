# Autom8 - Professional Systems Automation Toolkit

**Developer:** Alphonce Liguori Oreny  
**Project Type:** Systems Management & Automation  
**Tech Stack:** Python 3.14, Flask, SQLAlchemy, APScheduler, Docker  
**Status:** Active Development

## 📋 Project Overview

Autom8 is a production-grade automation system featuring:

- RESTful API for contact management
- SQLAlchemy ORM database layer
- Automated background job scheduling
- Structured logging & monitoring
- Containerized deployment with Docker
- Comprehensive test coverage (80%+)

## 🏗️ Architecture

```
autom8/
├── core.py        # Shared utilities, config, logging
├── models.py      # SQLAlchemy ORM models
├── api.py         # Flask REST API endpoints
└── scheduler.py   # APScheduler background jobs
```

## 🚀 Quick Start

**Requirements:**

- Python 3.9+
- Virtual environment recommended
- Docker (optional, for containerized deployment)

## 📦 Installation

**Clone repository:**

```bash
git clone https://github.com/orenyalphy256-glitch/op-alpha-systems-automation.git
cd op-alpha-systems-automation
```

**Create virtual environment:**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

**Install in editable mode:**

```bash
pip install -e .
```

## 🔌 API Usage

**Running Services:**

- **API only:** `python run_api.py`
- **Combined (API + Scheduler):** `python run_combined.py`
- **Real-time monitoring dashboard:** `python -m autom8.monitor_scheduler`
- **DB-Init Service:** One-time database initialization

**API Endpoints:**

```bash
# List contacts
curl http://localhost:5000/api/v1/contacts

# Create contact
curl -X POST http://localhost:5000/api/v1/contacts \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","phone":"0712345678"}'

# Update contact
curl -X PUT http://localhost:5000/api/v1/contacts/1 \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com"}'

# Delete contact
curl -X DELETE http://localhost:5000/api/v1/contacts/1

# View all metrics
curl http://localhost:5000/api/v1/metrics

# System metrics only
curl http://localhost:5000/api/v1/metrics/system

# Detailed health check
curl http://localhost:5000/api/v1/health/detailed
```

## 🧪 Testing

### Test Suite

Autom8 has comprehensive test coverage with both unit and integration tests.

**Test Structure:**

```
tests/
├── unit/                 # Fast, isolated tests
│   ├── test_models.py    # Database models
│   ├── test_core.py      # Core utilities
│   └── test_tasks.py     # Task functions
└── integration/          # Tests with dependencies
    ├── test_api.py       # API endpoints
    └── test_database.py  # Database operations
```

### Running Tests

**Quick Commands:**

```bash
# All tests with coverage
run-tests.bat

# Unit tests only (fast)
run-tests-unit.bat

# Integration tests only
run-tests-integration.bat

# Quick run (stop on first failure)
run-tests-quick.bat

# Watch mode (auto-rerun on changes)
run-tests-watch.bat
```

**Manual Pytest Commands:**

```bash
# All tests
pytest

# With coverage
pytest --cov=autom8 --cov-report=html

# Specific test file
pytest tests/unit/test_models.py

# Specific test
pytest tests/unit/test_models.py::test_contact_creation

# Only unit tests
pytest -m unit

# Skip slow tests
pytest -m "not slow"
```

### Coverage

**Current Coverage:** 80%+ (target achieved)

**View Coverage:**

- **Terminal:** `pytest --cov=autom8 --cov-report=term-missing`
- **HTML Report:** `htmlcov/index.html` (after running tests)
- **XML:** `coverage.xml` (for CI/CD)

**Coverage Requirements:**

- Minimum: 70%
- Target: 80%
- Goal: 90%+

### Test Philosophy

- **Unit Tests (70%):** Fast, isolated, test individual functions
- **Integration Tests (30%):** Test component interactions
- **TDD Approach:** Write tests first, then code
- **Fixtures:** Reusable setup code in `conftest.py`
- **Mocking:** Mock external dependencies (email, SMS, APIs)

**For detailed testing guide, see:** `TESTING_GUIDE.md`

## 🐳 Docker Deployment

### Quick Docker Commands

```bash
# Test configuration
docker-test.bat

# Start all services
docker-start.bat

# Check status
docker-status.bat

# Rebuild
docker-rebuild.bat

# Scale API
docker-scale.bat
```

### Docker Compose

**Development:**

```bash
# Build and run
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

**Production:**

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
# - Optimized for production
# - Strict resource limits
# - Always restart policy
```

### Manual Docker Commands

```bash
# Build image
docker build -t autom8:latest .

# Run container
docker run -d \
  --name autom8_api \
  -p 5000:5000 \
  -v autom8_data:/app/data \
  -v autom8_logs:/app/logs \
  autom8:latest

# View logs in real-time
docker logs -f autom8_api

# Stop container
docker stop autom8_api
```

## 📊 Monitoring & Logging

**Logging Example:**

```python
# Logging example
log.info("System initialized")

# JSON operations
data = {"name": "Alphonce", "role": "Engineer"}
save_json("output.json", data)
```

**Features:**

- Advanced structured logging (JSON/text/errors)
- Log rotation and management
- System metrics (task stats, database stats)
- Health check endpoints with detailed metrics
- Email alerting on task failures
- Real-time monitoring dashboard
- Log analysis tools

## 📝 Development Log

### Phase 1: Foundation

- Project structure established
- Core utilities module implemented
- Logging infrastructure configured
- Package installation setup (setup.py)

### Phase 2: Task System

- Task system with Factory pattern
- Abstract base class for extensibility
- BackupTask, CleanupTask, ReportTask implemented
- Unit tests with pytest

### Phase 3: Database Layer

- SQLAlchemy ORM integration
- Contact and TaskLog models defined
- CRUD helper functions implemented
- Database initialization and seeding
- Interactive database shell

### Phase 4: REST API

- Flask REST API with full CRUD operations
- RESTful endpoint design (GET, POST, PUT, DELETE)
- Request validation and error handling
- Pagination and search functionality
- Health check and API documentation

### Phase 5: Automation & Scheduling

- APScheduler integration for job automation
- Background management API endpoints
- Combined service (API + Scheduler)
- Real-time monitoring dashboard

### Phase 6: Monitoring & Alerting

- Advanced structured logging (JSON/text/errors)
- Log rotation and management
- System metrics (tasks stats, database stats)
- Health check endpoints with detailed metrics
- Email alerting on task failures
- Real-time monitoring dashboard
- Log analysis tools

### Phase 7: Containerization

- Docker containerization setup
- Created Dockerfile with multi-stage optimization
- Implemented Docker Compose for multi-service orchestration
- Volume management for persistent data
- Container networking configuration
- Health checks and monitoring
- Helper scripts for container management

### Phase 8: Testing & Quality Assurance

- Comprehensive test suite (unit + integration)
- Achieved 80%+ code coverage
- Test automation with pytest
- Coverage reporting (HTML, XML, terminal)
- Test fixtures and mocking strategies
- Continuous testing workflow
- Created TESTING_GUIDE.md documentation

## 📄 License

MIT License - See LICENSE file for details

## 📧 Contact

**Email:** orenyalphy256@gmail.com  
**Portfolio:** https://github.com/orenyalphy256-glitch/
