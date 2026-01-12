# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""

api.py - Flask REST API for Contact Management
Implements: RESTful endpoints using SQLAlchemy ORM
"""

import time
from datetime import datetime

from flask import Flask, abort, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy.exc import IntegrityError

from autom8 import scheduler as scheduler_provider
from autom8 import security
from autom8.core import LOGS_DIR, log
from autom8.metrics import get_all_metrics, get_system_metrics
from autom8.models import (
    Contact,
    SessionLocal,
    TaskLog,
    get_contact_by_id,
    serialize_contact,
    get_contact_by_phone,
    get_session,
    update_contact,
)
from autom8.performance import (
    cached,
    check_system_health,
    get_system_performance,
    perf_monitor,
    timed_cache,
)
from autom8.security import SecurityConfig
from autom8.config import Config
from autom8.ownership import OwnershipAuthority

# Flask Application Setup
app = Flask(__name__)

# Configuration from the environment
app.config.from_object("autom8.config.Config")

# Rate Limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[SecurityConfig.RATE_LIMIT_DEFAULT],
    storage_uri=SecurityConfig.RATE_LIMIT_STORAGE if SecurityConfig.RATE_LIMIT_STORAGE else None,
    enabled=SecurityConfig.RATE_LIMIT_ENABLED,
    swallow_errors=True,
    strategy="fixed-window",
)


# Security Headers


# Error Handlers
@app.errorhandler(400)
def bad_request(error):
    return (
        jsonify(
            {
                "error": "Bad Request",
                "message": (
                    str(error.description) if hasattr(error, "description") else "Invalid request"
                ),
            }
        ),
        400,
    )


@app.errorhandler(401)
def unauthorized_handler(e):
    """Handle unauthorized access."""
    return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401


@app.errorhandler(403)
def forbidden_handler(e):
    """Handle forbidden access."""
    return jsonify({"error": "Forbidden", "message": "Access denied"}), 403


@app.errorhandler(404)
def not_found(error):
    return (
        jsonify(
            {
                "error": "Not Found",
                "message": (
                    str(error.description)
                    if hasattr(error, "description")
                    else "Resource not found"
                ),
            }
        ),
        404,
    )


@app.errorhandler(409)
def conflict(error):
    return (
        jsonify(
            {
                "error": "Conflict",
                "message": (
                    str(error.description)
                    if hasattr(error, "description")
                    else "Resource already exists"
                ),
            }
        ),
        409,
    )


@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded."""
    security.log_security_event(
        "rate_limit_exceeded",
        {"endpoint": request.endpoint, "limit": str(e.description)},
        "WARNING",
    )

    return (
        jsonify(
            {
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
            }
        ),
        429,
    )


@app.errorhandler(500)
def internal_error(error):
    log.error(f"Internal server error: {error}")
    return (
        jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred"}),
        500,
    )


# Helper Functions
def _validate_name(name):
    if not isinstance(name, str) or not name.strip():
        return False, "Name must be a non-empty string"
    if len(name) > 100:
        return False, "Name must be 100 characters or less"
    return True, None


def _validate_phone(phone):
    if not isinstance(phone, str) or not phone.strip():
        return False, "Phone must be a non-empty string"
    if len(phone) > 20:
        return False, "Phone must be 20 characters or less"
    return True, None


def _validate_email(email):
    if not isinstance(email, str):
        return False, "Email must be a string"
    if len(email) > 100:
        return False, "Email must be 100 characters or less"
    if "@" not in email:
        return False, "Email must contain @ symbol"
    return True, None


def validate_contact_data(data, required_fields=None):
    """Validate contact data from request."""
    if not data:
        return False, "Request body must be JSON"

    if required_fields:
        missing = [field for field in required_fields if field not in data]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"

    """Validate contact name from request."""
    if "name" in data:
        valid, msg = _validate_name(data["name"])
        if not valid:
            return valid, msg

    """Validate contact phone number."""
    if "phone" in data:
        valid, msg = _validate_phone(data["phone"])
        if not valid:
            return valid, msg

    """Validate email (if provided)."""
    if "email" in data and data["email"]:
        valid, msg = _validate_email(data["email"])
        if not valid:
            return valid, msg

    return True, None


# API Routes - Contacts
@app.route("/api/v1/health", methods=["GET"])
@limiter.exempt  # No rate limit on health check
def health():
    """Health check endpoint."""
    return jsonify(
        {
            "status": "healthy",
            "service": Config.APP_NAME,
            "version": Config.APP_VERSION,
            "environment": Config.ENVIRONMENT,
        }
    )


@app.route("/api/v1/info", methods=["GET"])
@limiter.exempt
def info():
    """API information endpoint."""
    return jsonify(
        {
            "name": Config.APP_NAME,
            "version": Config.APP_VERSION,
            "environment": Config.ENVIRONMENT,
            "licensed": OwnershipAuthority.is_licensed(),
            "integrity": "verified" if OwnershipAuthority.integrity_verified() else "compromised",
            "security": {
                "rate_limiting": SecurityConfig.RATE_LIMIT_ENABLED,
                "cors_enabled": True,
                "https_only": False,
            },
            "documentation": "https://github.com/orenyalphy256-glitch/op-alpha-systems-automation",
        }
    )


@app.route("/api/v1/auth/login", methods=["POST"])
@limiter.limit("5 per minute")  # Strict rate limit on login
def login():
    """
    Demo login endpoint.
    """
    data = request.get_json()

    # Sanitize input using provider
    username = security.sanitize_input(data.get("username", ""))
    password = data.get("password", "")

    if not username or not password:
        security.log_security_event(
            "login_failed",
            {"username": username, "reason": "missing_credentials"},
            "WARNING",
        )
        return jsonify({"error": "Username and password required"}), 400

    # DEMO: In production, verify against database
    if username == "demo" and password == "password123":  # nosec B105 - Demo credentials only
        token = security.generate_token(username, {"role": "user"})

        try:
            from autom8.security import log_security_event

            log_security_event("login_success", {"username": username}, "INFO")
        except ImportError:
            log.info(f"Login success: {username}")

        return jsonify({"token": token, "username": username, "message": "Login successful"})

    security.log_security_event(
        "login_failed", {"username": username, "reason": "invalid_credentials"}, "WARNING"
    )

    return jsonify({"error": "Invalid credentials"}), 401


@app.route("/api/v1/auth/protected", methods=["GET"])
def protected():
    """
    Demo protected endpoint.
    Uses runtime token verification via provider.
    """
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        abort(401)

    try:
        token_val = token.split(" ")[1]
        current_user = security.verify_token(token_val)
    except Exception:
        abort(401)
    return jsonify(
        {
            "message": "Access granted to protected resource",
            "user": current_user.get("user_id"),
            "role": current_user.get("role"),
        }
    )


@app.route("/api/v1/contacts", methods=["GET"])
def get_contacts():
    limit_arg = request.args.get("limit")
    offset_arg = request.args.get("offset")

    result = _get_contacts_internal(limit_arg, offset_arg)
    return jsonify(result)


@cached(cache_obj=timed_cache)
def _get_contacts_internal(limit_arg, offset_arg):
    limit = int(limit_arg) if limit_arg else 100
    offset = int(offset_arg) if offset_arg else 0

    session = SessionLocal()
    try:
        query = session.query(Contact)
        total = query.count()

        contacts = query.order_by(Contact.name).offset(offset).limit(limit).all()

        contacts_list = [serialize_contact(c) for c in contacts]

        return {
            "contacts": contacts_list,
            "meta": {
                "total": total,
                "limit": limit,
                "offset": offset,
            },
        }
    finally:
        session.close()


# Clear cache helpers to be called after modifications
def clear_contacts_cache():
    _get_contacts_internal.cache_clear()


@app.route("/api/v1/contacts/<int:contact_id>", methods=["GET"])
@limiter.limit(SecurityConfig.RATE_LIMIT_CONTACTS_GET)
def get_contact(contact_id):
    """Get specific contact."""
    session = SessionLocal()
    try:
        contact = session.query(Contact).filter_by(id=contact_id).first()
        if not contact:
            return jsonify({"error": "Contact not found"}), 404

        return jsonify(serialize_contact(contact)), 200
    finally:
        session.close()


@app.route("/api/v1/contacts", methods=["POST"])
@limiter.limit(SecurityConfig.RATE_LIMIT_CONTACTS_POST)
def create_contact():
    """Create new contact with validation."""
    data = request.get_json()

    # Sanitize inputs
    name = security.sanitize_input(data.get("name", ""))
    phone = security.sanitize_input(data.get("phone", ""))

    # Validate
    if not name or not phone:
        return jsonify({"error": "Name and phone required"}), 400

    # Validate phone format using security module
    if not security.validate_phone(phone):
        security.log_security_event(
            "invalid_input",
            {"field": "phone", "value": phone, "endpoint": "/api/v1/contacts"},
            "WARNING",
        )
        return jsonify({"error": "Invalid phone number format"}), 400

    # Create contact
    session = SessionLocal()
    try:
        contact = Contact(name=name, phone=phone)
        session.add(contact)
        session.commit()

        # Cache will auto-expire per TTL, avoiding stampede during write-heavy tests

        log.info(f"Contact created: {name}")

        return (
            jsonify(serialize_contact(contact)),
            201,
        )
    except IntegrityError:
        session.rollback()
        log.warning(f"Attempt to create duplicate contact: {name} ({phone})")
        return jsonify({"error": "Contact with this phone number already exists"}), 409
    except Exception as e:
        session.rollback()
        log.error(f"Error creating contact: {e}")
        return jsonify({"error": "Failed to create contact"}), 500
    finally:
        session.close()


@app.route("/api/v1/contacts/<int:contact_id>", methods=["PUT"])
@limiter.limit(SecurityConfig.RATE_LIMIT_CONTACTS_PUT)
def update_contact_endpoint(contact_id):
    session = get_session()

    try:
        existing = get_contact_by_id(session, contact_id)
        if not existing:
            abort(404, description=f"Contact with ID {contact_id} not found")

        data = request.get_json()

        is_valid, error_msg = validate_contact_data(data)
        if not is_valid:
            abort(400, description=error_msg)

        if "phone" in data and data["phone"] != existing.phone:
            phone_conflict = get_contact_by_phone(session, data["phone"])
            if phone_conflict:
                abort(409, description=f"Contact with phone {data['phone']} already exists")

        updated = update_contact(session, contact_id, **data)

        # Cache will auto-expire per TTL, avoiding stampede during write-heavy tests

        log.info(f"Updated contact ID {contact_id}")

        return jsonify(serialize_contact(updated)), 200

    except IntegrityError as e:
        session.rollback()
        log.error(f"Integrity error updating contact: {e}")
        abort(409, description="Phone number already exists")

    finally:
        session.close()


@app.route("/api/v1/contacts/<int:contact_id>", methods=["DELETE"])
@limiter.limit(SecurityConfig.RATE_LIMIT_CONTACTS_DELETE)
def delete_contact(contact_id):
    """Delete contact."""
    session = SessionLocal()
    try:
        contact = session.query(Contact).filter_by(id=contact_id).first()
        if not contact:
            return jsonify({"error": "Contact not found"}), 404

        session.delete(contact)
        session.commit()

        # Cache will auto-expire per TTL, avoiding stampede during write-heavy tests

        log.info(f"Contact deleted: ID {contact_id}")

        return jsonify({"message": "Contact deleted"}), 200
    except Exception as e:
        session.rollback()
        log.error(f"Error deleting contact: {e}")
        return jsonify({"error": "Failed to delete contact"}), 500
    finally:
        session.close()


# Scheduler management endpoints
@app.route("/api/v1/scheduler/status", methods=["GET"])
def scheduler_status():
    if scheduler_provider is None:
        return jsonify({"running": False, "jobs": []}), 200
    return (
        jsonify({"running": True, "jobs": scheduler_provider.get_scheduled_jobs()}),
        200,
    )


@app.route("/api/v1/scheduler/jobs/<job_id>/run", methods=["POST"])
def trigger_job(job_id):
    try:
        scheduler_provider.run_job_now(job_id)
        log.info(f"Manually executed job {job_id} successfully")
        return (
            jsonify({"status": "success", "message": f"Job {job_id} triggered successfully"}),
            200,
        )
    except ValueError as e:
        abort(404, description=str(e))
    except Exception as e:
        log.error(f"Error triggering job {job_id}: {e}")
        abort(500)


@app.route("/api/v1/scheduler/jobs/<job_id>/pause", methods=["POST"])
def pause_job_endpoint(job_id):
    try:
        scheduler_provider.pause_job(job_id)
        log.info(f"Job {job_id} paused successfully")
        return jsonify({"status": "success", "message": f"Job {job_id} paused successfully"}), 200
    except Exception as e:
        log.error(f"Error pausing job {job_id}: {e}")
        abort(500)


@app.route("/api/v1/scheduler/jobs/<job_id>/resume", methods=["POST"])
def resume_job_endpoint(job_id):
    try:
        scheduler_provider.resume_job(job_id)
        log.info(f"Job {job_id} resumed successfully")
        return jsonify({"status": "success", "message": f"Job {job_id} resumed successfully"}), 200
    except Exception as e:
        log.error(f"Error resuming job {job_id}: {e}")
        abort(500)


@app.route("/api/v1/tasklogs", methods=["GET"])
def get_task_logs():
    session = get_session()

    try:
        # Get query parameters
        task_type = request.args.get("task_type", None)
        status = request.args.get("status", None)
        limit = request.args.get("limit", 50, type=int)

        # Build query
        query = session.query(TaskLog)

        if task_type:
            query = query.filter(TaskLog.task_type == task_type)

        if status:
            query = query.filter(TaskLog.status == status)

        # Order by most recent first
        query = query.order_by(TaskLog.started_at.desc())

        # Limit results
        logs = query.limit(limit).all()

        # Serialize
        result = [log.to_dict() for log in logs]

        return jsonify({"count": len(result), "logs": result}), 200

    finally:
        session.close()


@app.route("/api/v1/tasklogs/stats", methods=["GET"])
@cached(cache_obj=timed_cache)
def get_task_stats():
    session = get_session()

    try:
        total = session.query(TaskLog).count()
        completed = session.query(TaskLog).filter(TaskLog.status == "completed").count()
        failed = session.query(TaskLog).filter(TaskLog.status == "failed").count()
        running = session.query(TaskLog).filter(TaskLog.status == "running").count()

        # Success rate
        success_rate = (completed / total * 100) if total > 0 else 0

        return (
            jsonify(
                {
                    "total_executions": total,
                    "completed": completed,
                    "failed": failed,
                    "running": running,
                    "success_rate": round(success_rate, 2),
                }
            ),
            200,
        )

    finally:
        session.close()


# Monitoring & Metrics Endpoints
@app.route("/api/v1/metrics", methods=["GET"])
@limiter.exempt
def get_metrics():
    try:
        metrics = get_all_metrics()
        return jsonify(metrics), 200
    except Exception as e:
        log.error(f"Error fetching metrics: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/metrics/system", methods=["GET"])
@limiter.exempt
def get_system_metrics_endpoint():
    """Get system metric only."""
    try:
        metrics = get_system_metrics()
        return jsonify(metrics), 200
    except Exception as e:
        log.error(f"Error fetching system metrics: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/logs/errors", methods=["GET"])
@limiter.exempt
def get_error_logs():
    try:
        limit = request.args.get("limit", 50, type=int)

        # Read error log file
        error_log_path = LOGS_DIR / f"{Config.APP_NAME}_errors.log"

        if not error_log_path.exists():
            return jsonify({"errors": []}), 200

        with open(error_log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Get last N lines
        recent_errors = lines[-limit:] if len(lines) > limit else lines

        return (
            jsonify(
                {"count": len(recent_errors), "errors": [line.strip() for line in recent_errors]}
            ),
            200,
        )

    except Exception as e:
        log.error(f"Error reading error logs: {e}")
        return jsonify({"error": str(e)}), 500


# PERFORMANCE ENDPOINTS
@app.route("/api/v1/performance/stats", methods=["GET"])
@limiter.exempt  # No rate limit on performance monitoring
def performance_stats():
    """Get performance stats."""
    stats = perf_monitor.get_stats()
    return jsonify(stats)


@app.route("/api/v1/performance/system", methods=["GET"])
@limiter.exempt
def system_performance():
    """Get current system performance metrics."""
    metrics = get_system_performance()
    return jsonify(metrics)


@app.route("/api/v1/performance/health", methods=["GET"])
@limiter.exempt
def system_health():
    """Check system health status."""
    health = check_system_health()
    return jsonify(health)


@app.route("/api/v1/performance/cache/clear", methods=["POST"])
@limiter.limit("20 per minute")  # Increased limit for cache clearing
def clear_cache():
    """Clear application cache."""
    from autom8.performance import function_cache, timed_cache

    function_cache.clear()
    timed_cache.clear()

    log.info("Application cache cleared")

    return jsonify(
        {"message": "Cache cleared successfully", "timestamp": datetime.now().isoformat()}
    )


# Request timing middleware
@app.before_request
def before_request():
    """Start timer for request."""
    from flask import g

    g.start_time = time.time()


@app.after_request
def after_request(response):
    """Record request duration and add security headers."""
    from flask import g

    # Add security headers
    security.add_security_headers(response)

    if hasattr(g, "start_time"):
        duration = time.time() - g.start_time
        endpoint = request.endpoint or "unknown"
        perf_monitor.record_request(endpoint, duration)

        # Add performance header
        response.headers["X-Response-Time"] = f"{duration:.4f}s"
        # Add proprietary heartbeat for integrity monitoring
        response.headers["X-Autom8-Integrity"] = (
            "ok" if OwnershipAuthority.is_licensed() else "unlicensed"
        )

    return response


# Root Endpoint
@app.route("/", methods=["GET"])
@limiter.exempt
def index():
    """
    API root - shows available endpoints.
    """
    return (
        jsonify(
            {
                "service": "Autom8 API",
                "version": "1.0",
                "endpoints": {
                    "health": "/api/v1/health",
                    "contacts": {
                        "list": "GET /api/v1/contacts",
                        "get": "GET /api/v1/contacts/{id}",
                        "create": "POST /api/v1/contacts",
                        "update": "PUT /api/v1/contacts/{id}",
                        "delete": "DELETE /api/v1/contacts/{id}",
                    },
                    "scheduler": {
                        "status": "GET /api/v1/scheduler/status",
                        "trigger_job": "POST /api/v1/scheduler/jobs/{job_id}/run",
                        "pause_job": "POST /api/v1/scheduler/jobs/{job_id}/pause",
                        "resume_job": "POST /api/v1/scheduler/jobs/{job_id}/pause",
                    },
                    "task_logs": {
                        "list": "GET /api/v1/task_logs",
                        "stats": "GET /api/v1/task_logs/stats",
                    },
                    "metrics": {
                        "get_metrics": "GET /api/v1/metrics",
                        "get_system_metrics_endpoint": "GET /api/v1/metrics/system",
                        "get_error_logs": "GET /api/v1/logs/errors",
                    },
                    "documentation": (
                        "https://github.com/orenyalphy256-glitch/op-alpha-systems-automation"
                    ),
                },
            }
        ),
        200,
    )


# MAIN
def main():
    """Entry point for console script."""
    log.info(f"Starting {Config.APP_NAME} API v{Config.APP_VERSION}")
    log.info(f"Environment: {Config.ENVIRONMENT}")
    log.info(f"Debug mode: {Config.DEBUG}")
    log.info(f"Rate limiting: {SecurityConfig.RATE_LIMIT_ENABLED}")

    app.run(host=Config.API_HOST, port=Config.API_PORT, debug=Config.DEBUG)


if __name__ == "__main__":
    main()
