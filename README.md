# Autom8 -Professional Systems Automation Toolkit

Developer: Alphonce Liguori Oreny
Project Type: Systems Management & Automation
Tech Stack: Python 3.14, Flask, SQLAlchemy, Docker
Status: Active Development (Batch 5)

## Project Overview

Autom8 is a production-grade automation system featuring:
-RESTful API for contact management
-SQLAlchemy ORM database layer
-Automated background job scheduling
-Structured logging & monitoring
-Containerized deployment with Docker

## Architecture

autom8/
├── core.py        # Shared utilities, config, logging
├── models.py      # SQLAlchemy ORM models
├── api.py         # Flask REST API endpoints
└── scheduler.py   # APScheduler background jobs

## Quick Start

- Python 3.9+
- Virtual environment recommended
- Dependencies

## Installation

** Clone repository
git clone <https://github.com/orenyalphy256-glitch/op-alpha-systems-automation.git>
cd op-alpha-systems-automation

## Create virtual environment

python -m venv venv
venv\Scripts\activate

** source venv/bin/activate # Linux/Mac

** Install in editable mode
pip install -e

## API Usage

- API only: python run_api.py
- Combined (API + Scheduler): python run_combined.py
- Real-time monitoring dashboard: python -m autom8.monitor_scheduler

## Example Usage

bash
** List contacts
curl <http://localhost:5000/api/v1/contacts>

** Create contact
curl -X POST <http://localhost:5000/api/v1/contacts> \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","phone":"0712345678"}'

** Update contact
curl -X PUT <http://localhost:5000/api/v1/contacts/1> \
  -H "Content-Type: application/json" \
  -d '{"email":"<john@example.com>"}'

** Delete contact
curl -X DELETE <http://localhost:5000/api/v1/contacts/1>

** View all metrics
curl http://localhost:5000/api/v1/metrics

** System metrics only
curl http://localhost:5000/api/v1/metrics/system

** Detailed health check
curl http://localhost:5000/api/v1/health/detailed

## Logging Example

** Logging example
log.info("System initialized")

## JSON operations

data = {"name": "Alphonce", "role": "Engineer"}
save_json("output.json", data)

## Development Log

- Project structure established
- Core utilities module implemented
- Logging infrastructure configured
- Package installation setup (setup.py)
- Task system with Factory pattern
- Abstract base class for extensibility
- BackupTask, CleanupTask, ReportTask implemented
- Unit tests with pytest
- SQLAlchemy ORM integration
- Contact and TaskLog models defined
- CRUD helper functions implemented
- Database initialization and seeding
- Interactive database shell
- Flask REST API with full CRUD operations
- RESTful endpoint design (GET, POST, PUT, DELETE)
- Request validation and error handling
- Pagination and search functionality
- Comprehensive automated tests (17 test cases)
- Health check and API documentation
- APScheduler integration for job automation
- Background management API endpoints
- Combined service (API + Scheduler)
- Real-time monitoring dashboard
- Advanced structured logging (JSON/text/errors)
- Log rotation and management
- System metrics (tasks stats, database stats)
- Health check endpoints with detailed metrics
- Email alerting on task failures
- Real-time monitoring dashboard
- Log analysis tools

## License

MIT License - See LICENSE file for details

## Contact Details

Contact email: <orenyalphy256@gmail.com>
Portfolio: <https://github.com/orenyalphy256-glitch/>
