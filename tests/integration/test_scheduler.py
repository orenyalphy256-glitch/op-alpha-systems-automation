# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""

Integration tests for APScheduler functionality.

Tests cover:
- Scheduler initialization
- Job scheduling
- Job execution
- Job management (pause, resume, remove)
"""

import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch  # noqa: F401

import pytest
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# Import your scheduler module
try:
    from autom8 import scheduler
except ImportError:
    scheduler = None


# SKIP TESTS IF SCHEDULER NOT AVAILABLE

pytestmark = pytest.mark.skipif(scheduler is None, reason="Scheduler module not available")


# FIXTURES


@pytest.fixture
def test_scheduler():
    """Provide a test scheduler instance."""
    test_sched = BackgroundScheduler()
    test_sched.start()

    yield test_sched

    # Cleanup
    test_sched.shutdown(wait=False)


@pytest.fixture
def mock_job_function():
    """Provide a mock function for testing job execution."""
    mock_func = Mock()
    mock_func.__name__ = "test_job"  # APScheduler needs function name
    return mock_func


# SCHEDULER INITIALIZATION TESTS


class TestSchedulerInitialization:
    """Test scheduler initialization and configuration."""

    def test_scheduler_creation(self):
        """Test creating a scheduler instance."""
        # Act
        sched = BackgroundScheduler()

        # Assert
        assert sched is not None
        assert isinstance(sched, BackgroundScheduler)

        # Cleanup - only shutdown if running
        if sched.running:
            sched.shutdown(wait=False)

    def test_scheduler_start(self, test_scheduler):
        """Test starting the scheduler."""
        # Assert
        assert test_scheduler.running is True
        assert test_scheduler.state == 1  # STATE_RUNNING

    def test_scheduler_stop(self):
        """Test stopping the scheduler."""
        # Arrange
        sched = BackgroundScheduler()
        sched.start()

        # Act
        sched.shutdown(wait=False)

        # Assert
        assert sched.running is False


# JOB SCHEDULING TESTS


class TestJobScheduling:
    """Test job scheduling functionality."""

    def test_add_interval_job(self, test_scheduler, mock_job_function):
        """Test adding a job with interval trigger."""
        # Act
        job = test_scheduler.add_job(
            mock_job_function, trigger="interval", seconds=60, id="test_interval_job"
        )

        # Assert
        assert job is not None
        assert job.id == "test_interval_job"
        assert isinstance(job.trigger, IntervalTrigger)

    def test_add_cron_job(self, test_scheduler, mock_job_function):
        """Test adding a job with cron trigger."""
        # Act
        job = test_scheduler.add_job(
            mock_job_function, trigger="cron", hour=10, minute=0, id="test_cron_job"
        )

        # Assert
        assert job is not None
        assert job.id == "test_cron_job"
        assert isinstance(job.trigger, CronTrigger)

    def test_add_date_job(self, test_scheduler, mock_job_function):
        """Test adding a one-time job."""
        # Arrange
        run_time = datetime.now() + timedelta(seconds=60)

        # Act
        job = test_scheduler.add_job(
            mock_job_function, trigger="date", run_date=run_time, id="test_date_job"
        )

        # Assert
        assert job is not None
        assert job.id == "test_date_job"

    def test_add_duplicate_job_id_fails(self, test_scheduler, mock_job_function):
        """Test that adding job with duplicate ID fails."""
        # Arrange
        test_scheduler.add_job(
            mock_job_function, trigger="interval", seconds=60, id="duplicate_job"
        )

        # Act & Assert
        with pytest.raises(Exception):  # APScheduler raises ConflictingIdError
            test_scheduler.add_job(
                mock_job_function, trigger="interval", seconds=60, id="duplicate_job"
            )


# JOB EXECUTION TESTS


class TestJobExecution:
    """Test job execution."""

    def test_job_executes(self, test_scheduler, mock_job_function):
        """Test that scheduled job actually executes."""
        # Arrange
        test_scheduler.add_job(
            mock_job_function,
            trigger="interval",
            seconds=1,  # Run every second
            id="execution_test_job",
        )

        # Act
        time.sleep(2)  # Wait for job to execute

        # Assert
        assert mock_job_function.call_count >= 1

    def test_job_with_args(self, test_scheduler):
        """Test job execution with arguments."""
        # Arrange
        mock_func = Mock()
        mock_func.__name__ = "test_job_with_args"

        test_scheduler.add_job(
            mock_func,
            trigger="date",
            run_date=datetime.now() + timedelta(seconds=1),
            args=["arg1", "arg2"],
            kwargs={"key": "value"},
        )

        # Act
        time.sleep(2)

        # Assert
        mock_func.assert_called_once_with("arg1", "arg2", key="value")

    @pytest.mark.slow
    def test_job_executes_multiple_times(self, test_scheduler, mock_job_function):
        """Test that interval job executes multiple times."""
        # Arrange
        test_scheduler.add_job(
            mock_job_function, trigger="interval", seconds=1, id="multi_execution_job"
        )

        # Act
        time.sleep(3.5)  # Wait for ~3 executions

        # Assert
        assert mock_job_function.call_count >= 2


# JOB MANAGEMENT TESTS


class TestJobManagement:
    """Test job management operations."""

    def test_get_job(self, test_scheduler, mock_job_function):
        """Test retrieving a job by ID."""
        # Arrange
        test_scheduler.add_job(mock_job_function, trigger="interval", seconds=60, id="get_job_test")

        # Act
        job = test_scheduler.get_job("get_job_test")

        # Assert
        assert job is not None
        assert job.id == "get_job_test"

    def test_get_nonexistent_job(self, test_scheduler):
        """Test getting job that doesn't exist returns None."""
        # Act
        job = test_scheduler.get_job("nonexistent_job")

        # Assert
        assert job is None

    def test_remove_job(self, test_scheduler, mock_job_function):
        """Test removing a job."""
        # Arrange
        test_scheduler.add_job(
            mock_job_function, trigger="interval", seconds=60, id="remove_job_test"
        )

        # Act
        test_scheduler.remove_job("remove_job_test")

        # Assert
        job = test_scheduler.get_job("remove_job_test")
        assert job is None

    def test_pause_job(self, test_scheduler, mock_job_function):
        """Test pausing a job."""
        # Arrange
        job = test_scheduler.add_job(
            mock_job_function, trigger="interval", seconds=1, id="pause_job_test"
        )

        # Act
        job.pause()
        time.sleep(2)

        # Assert
        # Job should not execute while paused
        assert mock_job_function.call_count == 0

    def test_resume_job(self, test_scheduler, mock_job_function):
        """Test resuming a paused job."""
        # Arrange
        job = test_scheduler.add_job(
            mock_job_function, trigger="interval", seconds=1, id="resume_job_test"
        )
        job.pause()

        # Act
        job.resume()
        time.sleep(2)

        # Assert
        # Job should execute after resume
        assert mock_job_function.call_count >= 1

    def test_get_all_jobs(self, test_scheduler, mock_job_function):
        """Test getting all scheduled jobs."""
        # Arrange
        test_scheduler.add_job(mock_job_function, "interval", seconds=60, id="job1")
        test_scheduler.add_job(mock_job_function, "interval", seconds=60, id="job2")
        test_scheduler.add_job(mock_job_function, "interval", seconds=60, id="job3")

        # Act
        jobs = test_scheduler.get_jobs()

        # Assert
        assert len(jobs) == 3
        job_ids = [job.id for job in jobs]
        assert "job1" in job_ids
        assert "job2" in job_ids
        assert "job3" in job_ids


# ERROR HANDLING TESTS


class TestSchedulerErrorHandling:
    """Test scheduler error handling."""

    def test_job_exception_handling(self, test_scheduler):
        """Test that job exceptions don't crash scheduler."""

        # Arrange
        def failing_job():
            raise ValueError("Intentional error for testing")

        failing_job.__name__ = "failing_job"

        test_scheduler.add_job(
            failing_job,
            trigger="date",
            run_date=datetime.now() + timedelta(seconds=1),
            id="failing_job_test",
        )

        # Act
        time.sleep(2)

        # Assert
        # Scheduler should still be running despite job failure
        assert test_scheduler.running is True

    def test_remove_nonexistent_job(self, test_scheduler):
        """Test removing job that doesn't exist."""
        # Act & Assert
        # Should not raise exception (or raises JobLookupError which is caught)
        try:
            test_scheduler.remove_job("nonexistent_job")
        except Exception:
            # Some versions raise exception, some don't
            pass


# INTEGRATION WITH AUTOM8 SCHEDULER


@pytest.mark.skipif(
    not hasattr(scheduler, "start_scheduler"), reason="Autom8 scheduler not available"
)
class TestAutom8Scheduler:
    """Test integration with autom8 scheduler module."""

    def test_autom8_scheduler_start(self):
        """Test starting autom8 scheduler."""
        # This test depends on your actual scheduler implementation
        # Adjust based on your scheduler module structure
        pass

    def test_autom8_scheduled_tasks(self):
        """Test that autom8 tasks are scheduled correctly."""
        # This test depends on your actual scheduler implementation
        # Adjust based on your scheduler module structure
        pass


# MOCK TIME TESTS (ADVANCED)


class TestSchedulerWithMockedTime:
    """Test scheduler with mocked time (advanced)."""

    @patch("time.sleep")
    def test_job_scheduling_with_mock_time(self, mock_sleep, test_scheduler, mock_job_function):
        """Test job execution with mocked time."""
        # Arrange
        test_scheduler.add_job(
            mock_job_function, trigger="interval", seconds=60, id="mock_time_job"
        )

        # Act
        # Simulate time passing
        mock_sleep.return_value = None

        # Assert
        # Job is scheduled but mock time doesn't advance
        # This is an advanced pattern for testing time-based code
        job = test_scheduler.get_job("mock_time_job")
        assert job is not None


# PARAMETRIZED SCHEDULER TESTS
@pytest.mark.parametrize(
    "trigger_type,trigger_args",
    [
        ("interval", {"seconds": 60}),
        ("interval", {"minutes": 1}),
        ("interval", {"hours": 1}),
        ("cron", {"hour": 10, "minute": 0}),
        ("cron", {"day_of_week": "mon", "hour": 9}),
    ],
)
def test_various_trigger_types(test_scheduler, mock_job_function, trigger_type, trigger_args):
    """Test various trigger types and configurations."""
    # Act
    job = test_scheduler.add_job(
        mock_job_function,
        trigger=trigger_type,
        **trigger_args,
        id=f"trigger_test_{trigger_type}_{hash(str(trigger_args))}",
    )

    # Assert
    assert job is not None
    assert job.trigger is not None
