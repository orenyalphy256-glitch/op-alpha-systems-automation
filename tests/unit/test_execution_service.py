# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.

import unittest
from unittest.mock import MagicMock, patch
from autom8.services.execution_service import ExecutionService


class TestExecutionService(unittest.TestCase):

    @patch("autom8.services.execution_service.get_session")
    @patch("autom8.services.execution_service.run_task")
    @patch("autom8.services.execution_service.TaskLog")
    def test_execution_success(self, mock_task_log_cls, mock_run, mock_get_session):
        # Setup
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        # Instance created by TaskLog(...)
        task_log_instance = MagicMock()
        task_log_instance.id = 1  # Integer ID for truthiness
        mock_task_log_cls.return_value = task_log_instance

        # Mocking session.refresh to do nothing (it would set the real ID in prod)
        mock_session.refresh.return_value = None

        # Behavior for finalization query
        mock_session.query.return_value.get.return_value = task_log_instance

        mock_run.return_value = {"status": "success", "data": "test"}

        # Test
        result = ExecutionService.execute_task("backup")

        # Assertions
        self.assertEqual(result["status"], "success")
        self.assertEqual(task_log_instance.status, "completed")
        mock_session.commit.assert_called()
        mock_session.close.assert_called()

    @patch("autom8.services.execution_service.get_session")
    @patch("autom8.services.execution_service.run_task")
    @patch("autom8.services.execution_service.TaskLog")
    @patch("autom8.services.execution_service.alert_task_failure")
    def test_execution_failure_with_alert(
        self, mock_alert, mock_task_log_cls, mock_run, mock_get_session
    ):
        # Setup
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        task_log_instance = MagicMock()
        task_log_instance.id = 2
        mock_task_log_cls.return_value = task_log_instance

        mock_session.query.return_value.get.return_value = task_log_instance

        mock_run.return_value = {"status": "failed", "error": "test error"}

        # Test
        result = ExecutionService.execute_task("backup")

        # Assertions
        self.assertEqual(result["status"], "failed")
        self.assertEqual(task_log_instance.status, "failed")
        mock_alert.assert_called_with("backup", "test error")
        mock_session.close.assert_called()

    @patch("autom8.services.execution_service.get_session", side_effect=Exception("DB Down"))
    @patch("autom8.services.execution_service.run_task")
    @patch("autom8.services.execution_service.ExecutionService._log_to_disk")
    def test_double_fault_protection(self, mock_disk_log, mock_run, mock_get_session):
        # Setup
        mock_run.return_value = {"status": "success"}

        # Test
        ExecutionService.execute_task("backup")

        # Assertions
        mock_disk_log.assert_called()
