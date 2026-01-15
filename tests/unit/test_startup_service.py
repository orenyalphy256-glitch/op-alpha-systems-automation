# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.

import unittest
from unittest.mock import MagicMock, patch
from autom8.services.startup_service import reconcile_zombie_tasks


class TestStartupService(unittest.TestCase):

    @patch("autom8.services.startup_service.get_session")
    def test_reconcile_zombies(self, mock_get_session):
        # Setup
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        zombie_task = MagicMock()
        zombie_task.status = "running"
        mock_session.query.return_value.filter.return_value.all.return_value = [zombie_task]

        # Test
        reconcile_zombie_tasks()

        # Assertions
        self.assertEqual(zombie_task.status, "interrupted")
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    @patch("autom8.services.startup_service.get_session")
    def test_reconcile_no_zombies(self, mock_get_session):
        # Setup
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_session.query.return_value.filter.return_value.all.return_value = []

        # Test
        reconcile_zombie_tasks()

        # Assertions
        mock_session.commit.assert_not_called()
        mock_session.close.assert_called_once()
