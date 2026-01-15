# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""
Advanced Unit Tests for Scheduler Logic
Covers init, start/stop, listeners, and job helpers.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from autom8 import scheduler
from autom8.scheduler import (
    get_scheduled_jobs,
    init_scheduler,
    job_error_listener,
    job_executed_listener,
    pause_job,
    remove_job,
    resume_job,
    run_job_now,
    schedule_backup_job,
    start_scheduler,
    stop_scheduler,
)


# Reset global scheduler before/after tests
@pytest.fixture(autouse=True)
def reset_scheduler():
    scheduler.scheduler = None
    yield
    scheduler.scheduler = None


@patch("autom8.scheduler.BackgroundScheduler")
def test_init_scheduler(mock_bg):
    # First init
    s = init_scheduler()
    assert s is not None
    mock_bg.assert_called_once()

    # Second init (should return existing)
    s2 = init_scheduler()
    assert s2 == s
    assert mock_bg.call_count == 1  # Still called once


def test_scheduler_lifecycle():
    mock_sched = MagicMock()
    scheduler.scheduler = mock_sched

    # Start
    mock_sched.running = False
    start_scheduler()
    mock_sched.start.assert_called_once()

    # Start again (noop)
    mock_sched.running = True
    start_scheduler()
    assert mock_sched.start.call_count == 1

    # Stop
    stop_scheduler()
    mock_sched.shutdown.assert_called_once()


def test_helpers_no_init():
    """Ensure helpers raise error if scheduler is missing."""
    scheduler.scheduler = None
    with pytest.raises(RuntimeError):
        schedule_backup_job()
    with pytest.raises(RuntimeError):
        start_scheduler()
    with pytest.raises(RuntimeError):
        pause_job("123")


def test_job_management():
    mock_sched = MagicMock()
    scheduler.scheduler = mock_sched

    # Pause
    pause_job("job1")
    mock_sched.pause_job.assert_called_with("job1")

    # Resume
    resume_job("job1")
    mock_sched.resume_job.assert_called_with("job1")

    # Remove
    remove_job("job1")
    mock_sched.remove_job.assert_called_with("job1")

    # Run Now
    # Setup mock job
    mock_job = MagicMock()
    mock_sched.get_job.return_value = mock_job
    mock_job.args = (1,)
    mock_job.kwargs = {"a": 2}

    run_job_now("job1")
    mock_job.func.assert_called_with(1, a=2)

    # Run Now (Not Found)
    mock_sched.get_job.return_value = None
    with pytest.raises(ValueError):
        run_job_now("bad_job")


def test_get_scheduled_jobs():
    scheduler.scheduler = None
    assert get_scheduled_jobs() == []

    mock_sched = MagicMock()
    scheduler.scheduler = mock_sched

    # Mock job objects
    j1 = MagicMock()
    j1.id = "j1"
    j1.name = "Job 1"
    j1.next_run_time = datetime(2025, 1, 1)
    j1.trigger = "interval"

    mock_sched.get_jobs.return_value = [j1]

    jobs = get_scheduled_jobs()
    assert len(jobs) == 1
    assert jobs[0]["id"] == "j1"


@patch("autom8.scheduler.log")
def test_listeners(mock_log):
    # Success listener
    event = MagicMock()
    event.job_id = "test_job"
    job_executed_listener(event)
    mock_log.info.assert_called()

    # Error listener
    event.exception = ValueError("Fail")
    job_error_listener(event)
    mock_log.error.assert_called()
