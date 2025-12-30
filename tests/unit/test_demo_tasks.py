# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

import pytest
from unittest.mock import patch, MagicMock
from autom8 import demo_tasks


def test_demo_tasks_main(capsys):
    """
    Test the main function of demo_tasks.py
    Verifies that:
    1. Task types are listed.
    2. Tasks are executed (backup, cleanup, report).
    3. Output is printed to stdout.
    """

    # Mock return values for run_task to avoid actual execution
    mock_results = {
        "backup": {"status": "success", "file": "backup_123.json", "timestamp": "20230101"},
        "cleanup": {"status": "success", "files_removed": 5, "space_freed": "10 MB"},
        "report": {"status": "success", "report_file": "report_123.json"},
    }

    def side_effect_run_task(task_type, name=None):
        return mock_results.get(task_type, {"status": "failed", "error": "Unknown type"})

    # Patch TaskFactory and run_task
    with (
        patch("autom8.demo_tasks.TaskFactory") as MockFactory,
        patch("autom8.demo_tasks.run_task", side_effect=side_effect_run_task) as mock_run,
    ):

        # Setup MockFactory.list_types
        MockFactory.list_types.return_value = ["backup", "cleanup", "report"]

        # Run main
        demo_tasks.main()

        # Capture output
        captured = capsys.readouterr()
        output = captured.out

        # Assertions

        # Check header
        assert "AUTOM8 TASK SYSTEM DEMONSTRATION" in output

        # Check if task types are listed
        assert "Available task types:" in output
        assert "- backup" in output
        assert "- cleanup" in output
        assert "- report" in output

        # Check execution logs
        assert "Executing tasks..." in output
        assert "Running BACKUP task" in output
        assert "Running CLEANUP task" in output
        assert "Running REPORT task" in output

        # Check status and details printing
        assert "Status: success" in output
        assert "file: backup_123.json" in output
        assert "files_removed: 5" in output
        # Verify run_task calls
        assert mock_run.call_count == 3
        mock_run.assert_any_call("backup")
        mock_run.assert_any_call("cleanup")
        mock_run.assert_any_call("report")


def test_demo_tasks_main_failure(capsys):
    """
    Test main function when a task fails.
    """
    with (
        patch("autom8.demo_tasks.TaskFactory") as MockFactory,
        patch("autom8.demo_tasks.run_task") as mock_run,
    ):

        MockFactory.list_types.return_value = ["backup"]
        mock_run.return_value = {"status": "failed", "error": "Disk full"}

        demo_tasks.main()

        captured = capsys.readouterr()
        output = captured.out

        assert "Status: failed" in output
        # Note: The code doesn't print details if status != success,
        # so we don't expect "error: Disk full" based on the current implementation of demo_tasks.py
