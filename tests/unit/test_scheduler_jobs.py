# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

from unittest.mock import MagicMock, patch

from autom8 import scheduler


@patch("autom8.scheduler.scheduler")
def test_schedule_helpers(mock_sched_obj):
    # Setup
    mock_sched_obj.add_job = MagicMock()

    # Test backup schedule
    scheduler.schedule_backup_job()
    args, kwargs = mock_sched_obj.add_job.call_args
    assert kwargs["func"] == scheduler.execute_task_with_logging
    assert kwargs["id"] == "backup_job"

    # Test cleanup schedule
    scheduler.schedule_cleanup_job()
    assert mock_sched_obj.add_job.call_count == 2

    # Test report schedule
    scheduler.schedule_report_job()
    assert mock_sched_obj.add_job.call_count == 3


@patch("autom8.scheduler.scheduler")
def test_start_scheduler_already_running(mock_sched_obj):
    mock_sched_obj.running = True
    result = scheduler.start_scheduler()
    assert result is None
    mock_sched_obj.start.assert_not_called()


@patch("autom8.scheduler.scheduler")
def test_stop_scheduler_not_running(mock_sched_obj):
    mock_sched_obj.running = False
    result = scheduler.stop_scheduler()
    assert result is None
    mock_sched_obj.shutdown.assert_not_called()
