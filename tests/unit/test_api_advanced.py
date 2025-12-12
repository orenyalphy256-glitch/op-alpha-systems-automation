"""
Advanced API Tests.
Covers edge cases, error handlers, and specific endpoint logic not covered by integration tests.
"""

from unittest.mock import MagicMock, patch

import pytest

from autom8.api import app, validate_contact_data


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ============================================================================
# Validation Tests
# ============================================================================


def test_validate_contact_data_edge_cases():
    # Not JSON (dict)
    assert validate_contact_data(None)[0] is False

    # Missing required
    assert validate_contact_data({}, required_fields=["name"])[0] is False

    # Invalid types
    assert validate_contact_data({"name": 123})[0] is False
    assert validate_contact_data({"phone": 123})[0] is False
    assert validate_contact_data({"email": 123})[0] is False

    # Length limits
    long_str = "a" * 101
    assert validate_contact_data({"name": long_str})[0] is False
    assert validate_contact_data({"email": long_str})[0] is False
    assert validate_contact_data({"phone": "1" * 21})[0] is False

    # Invalid Email
    assert validate_contact_data({"email": "no-at-symbol"})[0] is False


# ============================================================================
# Error Handler Tests
# ============================================================================

# ============================================================================
# Error Handler Tests
# ============================================================================


@patch("autom8.api.get_session")
def test_internal_server_error(mock_session, client):
    # Simulate a crash in an endpoint
    mock_session.side_effect = Exception("Crash!")

    # We must disable exception propagation to trigger the 500 handler
    app.config["PROPAGATE_EXCEPTIONS"] = False
    try:
        res = client.get("/api/v1/contacts")
        assert res.status_code == 500
        assert "Internal Server Error" in res.json["error"]
    finally:
        app.config["PROPAGATE_EXCEPTIONS"] = True


def test_404_handler(client):
    res = client.get("/api/v1/does-not-exist")
    assert res.status_code == 404
    assert "Not Found" in res.json["error"]


def test_405_handler(client):
    # POST to a GET-only endpoint
    res = client.post("/api/v1/health")
    assert res.status_code == 405


# ============================================================================
# Scheduler & Task Endpoint Tests (Mocked)
# ============================================================================


@patch("autom8.api.get_scheduled_jobs")
def test_scheduler_status(mock_get_jobs, client):
    # Mock the get_scheduled_jobs function which is imported by api
    mock_get_jobs.return_value = [{"id": "j1"}]

    # Patch the scheduler object in source module because api.py imports it locally
    with patch("autom8.scheduler.scheduler") as mock_sched:
        mock_sched.__bool__.return_value = True
        mock_sched.running = True
        res = client.get("/api/v1/scheduler/status")
        assert res.status_code == 200
        assert res.json["running"] is True


@patch("autom8.api.run_job_now")
def test_trigger_job(mock_run, client):
    # Success
    res = client.post("/api/v1/scheduler/jobs/j1/run")
    assert res.status_code == 200

    # Not Found
    mock_run.side_effect = ValueError("Job not found")
    res = client.post("/api/v1/scheduler/jobs/bad/run")
    assert res.status_code == 404

    # Error
    app.config["PROPAGATE_EXCEPTIONS"] = False
    try:
        mock_run.side_effect = Exception("Boom")
        res = client.post("/api/v1/scheduler/jobs/fail/run")
        assert res.status_code == 500
    finally:
        app.config["PROPAGATE_EXCEPTIONS"] = True


@patch("autom8.api.pause_job")
def test_pause_job_endpoint(mock_pause, client):
    res = client.post("/api/v1/scheduler/jobs/j1/pause")
    assert res.status_code == 200

    app.config["PROPAGATE_EXCEPTIONS"] = False
    try:
        mock_pause.side_effect = Exception("Fail")
        res = client.post("/api/v1/scheduler/jobs/j1/pause")
        assert res.status_code == 500
    finally:
        app.config["PROPAGATE_EXCEPTIONS"] = True


@patch("autom8.api.resume_job")
def test_resume_job_endpoint(mock_resume, client):
    res = client.post("/api/v1/scheduler/jobs/j1/resume")
    assert res.status_code == 200

    app.config["PROPAGATE_EXCEPTIONS"] = False
    try:
        mock_resume.side_effect = Exception("Fail")
        res = client.post("/api/v1/scheduler/jobs/j1/resume")
        assert res.status_code == 500
    finally:
        app.config["PROPAGATE_EXCEPTIONS"] = True


# ============================================================================
# Task Log Endpoint Tests
# ============================================================================


@patch("autom8.api.get_session")
def test_get_task_logs_filters(mock_session, client):
    # Setup mocks validation chaining
    mock_query = MagicMock()
    mock_session.return_value.query.return_value = mock_query

    # Make filter/order_by/limit return the same mock object (fluent interface)
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = []

    # Test filters applying
    client.get("/api/v1/tasklogs?task_type=backup&status=failed&limit=10")

    # Verify filter calls
    assert mock_query.filter.call_count == 2  # type and status


@patch("autom8.api.get_session")
def test_get_task_stats(mock_session, client):
    mock_q = MagicMock()
    mock_session.return_value.query.return_value = mock_q

    # Allow chaining for filters
    mock_q.filter.return_value = mock_q

    # When count() is called, return 10
    mock_q.count.return_value = 10

    res = client.get("/api/v1/tasklogs/stats")
    assert res.status_code == 200
    assert "success_rate" in res.json


# ============================================================================
# Metrics Endpoint Exceptions
# ============================================================================


@patch("autom8.api.get_all_metrics")
def test_metrics_error(mock_metrics, client):
    mock_metrics.side_effect = Exception("Metric fail")

    app.config["PROPAGATE_EXCEPTIONS"] = False
    try:
        res = client.get("/api/v1/metrics")
        assert res.status_code == 500
    finally:
        app.config["PROPAGATE_EXCEPTIONS"] = True


@patch("autom8.api.get_system_metrics")
def test_system_metrics_error(mock_sys, client):
    mock_sys.side_effect = Exception("Sys fail")

    app.config["PROPAGATE_EXCEPTIONS"] = False
    try:
        res = client.get("/api/v1/metrics/system")
        assert res.status_code == 500
    finally:
        app.config["PROPAGATE_EXCEPTIONS"] = True


def test_get_error_logs(client):
    # Case: Log file missing
    with patch("pathlib.Path.exists", return_value=False):
        res = client.get("/api/v1/logs/errors")
        assert res.json["errors"] == []

    # Case: Error reading
    with patch("pathlib.Path.exists", return_value=True):
        with patch("builtins.open", side_effect=Exception("Read fail")):
            app.config["PROPAGATE_EXCEPTIONS"] = False
            try:
                res = client.get("/api/v1/logs/errors")
                assert res.status_code == 500
            finally:
                app.config["PROPAGATE_EXCEPTIONS"] = True
