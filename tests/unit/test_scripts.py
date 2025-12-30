# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

from io import StringIO
from unittest.mock import MagicMock, patch

from autom8 import db_shell, init_database, inspect_db, seed_data

# ============================================================================
# init_database.py
# ============================================================================


def test_init_database():
    with patch("autom8.init_database.init_db") as mock_init:
        with patch("sys.stdout", new=StringIO()):
            init_database.main()
            mock_init.assert_called_once()


# ============================================================================
# seed_data.py
# ============================================================================


def test_seed_data():
    mock_db = MagicMock()
    with patch("autom8.seed_data.get_session", return_value=mock_db):
        with patch("autom8.seed_data.create_contact") as mock_create:
            seed_data.main()
            assert mock_create.call_count >= 3


# ============================================================================
# inspect_db.py
# ============================================================================


def test_inspect_db():
    mock_inspector = MagicMock()
    mock_inspector.get_table_names.return_value = ["contacts"]
    mock_inspector.get_columns.return_value = [{"name": "id", "type": "INTEGER"}]

    # We need to patch where it's used or simpler: just run main and ensure no crash
    mock_session = MagicMock()
    mock_session.query.return_value.count.return_value = 1

    with patch("autom8.inspect_db.get_session", return_value=mock_session):
        with patch("sys.stdout", new=StringIO()):
            # Also patch engine to avoid printing real url
            with patch("autom8.inspect_db.engine"):
                inspect_db.main()


# ============================================================================
# db_shell.py
# ============================================================================


def test_db_shell_main_session(capsys):
    mock_session = MagicMock()
    # Mock contacts list
    mock_contact = MagicMock()
    mock_contact.id = 1
    mock_contact.name = "Test User"
    mock_contact.phone = "123"

    mock_session.query.return_value.limit.return_value.offset.return_value.all.return_value = [
        mock_contact
    ]
    mock_session.query.return_value.filter.return_value.all.return_value = [mock_contact]

    with patch("autom8.db_shell.get_session", return_value=mock_session):
        # Scenario: list, search, unknown, quit
        inputs = ["list", "search", "Test", "unknown_cmd", "quit"]
        with patch("builtins.input", side_effect=inputs):
            db_shell.main()

    captured = capsys.readouterr()
    assert "AUTOM8 DATABASE SHELL" in captured.out
    assert "Test User" in captured.out
    assert "Unknown command" in captured.out


def test_db_shell_add_delete(capsys):
    mock_session = MagicMock()

    with patch("autom8.db_shell.get_session", return_value=mock_session):
        with patch("autom8.db_shell.create_contact") as mock_create:
            mock_create.return_value.id = 99
            with patch("autom8.db_shell.delete_contact", return_value=True):
                # Scenario: add, delete, quit
                inputs = ["add", "NewUser", "999", "e@mail.com", "delete", "99", "quit"]
                with patch("builtins.input", side_effect=inputs):
                    db_shell.main()

    captured = capsys.readouterr()
    assert "Created contact ID 99" in captured.out
    assert "Deleted contact ID 99" in captured.out
