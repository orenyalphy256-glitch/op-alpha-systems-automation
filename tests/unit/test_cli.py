# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""

Tests for autom8/cli.py

Comprehensive test suite for the CLI module to ensure 85%+ coverage.
"""

import pytest

from unittest.mock import Mock, patch, mock_open


# Import CLI module
from autom8 import cli


class TestPrintFunctions:
    """Test print utility functions"""

    def test_print_success(self, capsys):
        """Test print_success outputs correctly"""
        cli.print_success("Test message")
        captured = capsys.readouterr()
        assert "Test message" in captured.out
        assert "✓" in captured.out

    def test_print_error(self, capsys):
        """Test print_error outputs to stderr"""
        cli.print_error("Error message")
        captured = capsys.readouterr()
        assert "Error message" in captured.err
        assert "✗" in captured.err

    def test_print_info(self, capsys):
        """Test print_info outputs correctly"""
        cli.print_info("Info message")
        captured = capsys.readouterr()
        assert "Info message" in captured.out
        assert "ℹ" in captured.out

    def test_print_warning(self, capsys):
        """Test print_warning outputs correctly"""
        cli.print_warning("Warning message")
        captured = capsys.readouterr()
        assert "Warning message" in captured.out
        assert "⚠" in captured.out


class TestRunCommand:
    """Test run_command function"""

    @patch("subprocess.run")
    def test_run_command_success(self, mock_run):
        """Test successful command execution"""
        mock_run.return_value = Mock(returncode=0, stdout="output", stderr="")
        success, stdout, stderr = cli.run_command("test command")
        assert success is True
        assert stdout == "output"
        assert stderr == ""

    @patch("subprocess.run")
    def test_run_command_failure(self, mock_run):
        """Test failed command execution"""
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="error")
        success, stdout, stderr = cli.run_command("test command")
        assert success is False
        assert stderr == "error"

    @patch("subprocess.run")
    def test_run_command_exception(self, mock_run):
        """Test command execution with exception"""
        mock_run.side_effect = Exception("Test error")
        success, stdout, stderr = cli.run_command("test command")
        assert success is False
        assert "Test error" in stderr


class TestAPICommands:
    """Test API management commands"""

    @patch("builtins.open", new_callable=mock_open)
    @patch("autom8.cli.run_command")
    def test_cmd_api_start_success(self, mock_run, mock_file):
        """Test successful API start with PID file creation"""
        mock_run.return_value = (True, "output", "")
        args = Mock()
        result = cli.cmd_api_start(args)
        assert result == 0
        mock_run.assert_called_once()
        # Verify PID file was attempted to be written
        mock_file.assert_called()

    @patch("autom8.cli.run_command")
    def test_cmd_api_start_failure(self, mock_run):
        """Test failed API start"""
        mock_run.return_value = (False, "", "error")
        args = Mock()
        result = cli.cmd_api_start(args)
        assert result == 1

    @patch("os.remove")
    @patch("os.kill")
    @patch("builtins.open", new_callable=mock_open, read_data="1234")
    def test_cmd_api_stop_with_pid_file(self, mock_file, mock_kill, mock_remove):
        """Test API stop using PID file"""
        args = Mock()
        result = cli.cmd_api_stop(args)
        assert result == 0
        mock_kill.assert_called_once()
        mock_remove.assert_called()

    @patch("autom8.cli.run_command")
    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_cmd_api_stop_fallback_to_process_search(self, mock_file, mock_run):
        """Test API stop falls back to process search when PID file missing"""
        mock_run.return_value = (True, "", "")
        args = Mock()
        result = cli.cmd_api_stop(args)
        assert result == 0
        mock_run.assert_called_once()

    @patch("os.remove")
    @patch("os.kill", side_effect=ProcessLookupError)
    @patch("builtins.open", new_callable=mock_open, read_data="9999")
    @patch("autom8.cli.run_command")
    def test_cmd_api_stop_graceful_fails_then_fallback(
        self, mock_run, mock_file, mock_kill, mock_remove
    ):
        """Test API stop falls back when graceful shutdown fails"""
        mock_run.return_value = (True, "", "")
        args = Mock()
        result = cli.cmd_api_stop(args)
        assert result == 0
        mock_kill.assert_called_once()
        mock_run.assert_called_once()

    @patch("autom8.cli.cmd_api_stop")
    @patch("autom8.cli.cmd_api_start")
    def test_cmd_api_restart(self, mock_start, mock_stop):
        """Test API restart command"""
        mock_stop.return_value = 0
        mock_start.return_value = 0
        args = Mock()
        result = cli.cmd_api_restart(args)
        assert result == 0
        mock_stop.assert_called_once()
        mock_start.assert_called_once()

    @patch("requests.get")
    def test_cmd_api_status_running(self, mock_get):
        """Test API status when running"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"version": "1.0.0", "status": "healthy"}
        mock_get.return_value = mock_response

        args = Mock()
        result = cli.cmd_api_status(args)
        assert result == 0

    @patch("requests.get")
    def test_cmd_api_status_not_running(self, mock_get):
        """Test API status when not running"""
        mock_get.side_effect = Exception("Connection refused")
        args = Mock()
        result = cli.cmd_api_status(args)
        assert result == 1


class TestSchedulerCommands:
    """Test scheduler management commands"""

    @patch("autom8.cli.run_command")
    def test_cmd_scheduler_start_success(self, mock_run):
        """Test successful scheduler start"""
        mock_run.return_value = (True, "output", "")
        args = Mock()
        result = cli.cmd_scheduler_start(args)
        assert result == 0

    @patch("autom8.cli.run_command")
    def test_cmd_scheduler_start_failure(self, mock_run):
        """Test failed scheduler start"""
        mock_run.return_value = (False, "", "error")
        args = Mock()
        result = cli.cmd_scheduler_start(args)
        assert result == 1

    @patch("autom8.cli.run_command")
    def test_cmd_scheduler_stop(self, mock_run):
        """Test scheduler stop command"""
        mock_run.return_value = (True, "", "")
        args = Mock()
        result = cli.cmd_scheduler_stop(args)
        assert result == 0

    @patch("autom8.cli.run_command")
    @patch("sys.platform", "win32")
    def test_cmd_scheduler_status_running_windows(self, mock_run):
        """Test scheduler status on Windows when running"""
        mock_run.return_value = (True, "scheduler running", "")
        args = Mock()
        result = cli.cmd_scheduler_status(args)
        assert result == 0

    @patch("autom8.cli.run_command")
    def test_cmd_scheduler_status_not_running(self, mock_run):
        """Test scheduler status when not running"""
        mock_run.return_value = (True, "", "")
        args = Mock()
        result = cli.cmd_scheduler_status(args)
        assert result == 1


class TestDatabaseCommands:
    """Test database management commands"""

    @patch("autom8.cli.run_command")
    def test_cmd_db_init_success(self, mock_run):
        """Test successful database initialization"""
        mock_run.return_value = (True, "output", "")
        args = Mock()
        result = cli.cmd_db_init(args)
        assert result == 0

    @patch("autom8.cli.run_command")
    def test_cmd_db_init_failure(self, mock_run):
        """Test failed database initialization"""
        mock_run.return_value = (False, "", "error")
        args = Mock()
        result = cli.cmd_db_init(args)
        assert result == 1

    def test_cmd_db_migrate(self):
        """Test database migration command"""
        args = Mock()
        result = cli.cmd_db_migrate(args)
        assert result == 0

    @patch("autom8.cli.run_command")
    def test_cmd_db_seed_success(self, mock_run):
        """Test successful database seeding"""
        mock_run.return_value = (True, "output", "")
        args = Mock()
        result = cli.cmd_db_seed(args)
        assert result == 0

    @patch("autom8.cli.run_command")
    def test_cmd_db_seed_failure(self, mock_run):
        """Test failed database seeding"""
        mock_run.return_value = (False, "", "error")
        args = Mock()
        result = cli.cmd_db_seed(args)
        assert result == 1

    @patch("autom8.cli.run_command")
    def test_cmd_db_shell(self, mock_run):
        """Test database shell command"""
        mock_run.return_value = (True, "", "")
        args = Mock()
        result = cli.cmd_db_shell(args)
        assert result == 0

    @patch("autom8.cli.run_command")
    def test_cmd_db_backup_success(self, mock_run):
        """Test successful database backup"""
        mock_run.return_value = (True, "output", "")
        args = Mock()
        result = cli.cmd_db_backup(args)
        assert result == 0

    @patch("autom8.cli.run_command")
    def test_cmd_db_backup_failure(self, mock_run):
        """Test failed database backup"""
        mock_run.return_value = (False, "", "error")
        args = Mock()
        result = cli.cmd_db_backup(args)
        assert result == 1

    def test_cmd_db_restore_no_file(self):
        """Test database restore without file argument"""
        args = Mock(file=None)
        result = cli.cmd_db_restore(args)
        assert result == 1

    def test_cmd_db_restore_with_file(self):
        """Test database restore with file argument"""
        args = Mock(file="backup.sql")
        result = cli.cmd_db_restore(args)
        assert result == 0


class TestSystemCommands:
    """Test system operation commands"""

    @patch("autom8.cli.run_command")
    def test_cmd_health_success(self, mock_run):
        """Test successful health check"""
        mock_run.return_value = (True, "Health check output", "")
        args = Mock()
        result = cli.cmd_health(args)
        assert result == 0

    @patch("autom8.cli.run_command")
    def test_cmd_health_failure(self, mock_run):
        """Test failed health check"""
        mock_run.return_value = (False, "", "error")
        args = Mock()
        result = cli.cmd_health(args)
        assert result == 1

    @patch("requests.get")
    def test_cmd_info_api_running(self, mock_get):
        """Test system info when API is running"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        args = Mock()
        result = cli.cmd_info(args)
        assert result == 0

    @patch("requests.get")
    def test_cmd_info_api_not_running(self, mock_get):
        """Test system info when API is not running"""
        mock_get.side_effect = Exception("Connection refused")
        args = Mock()
        result = cli.cmd_info(args)
        assert result == 0

    @patch("requests.get")
    def test_cmd_metrics_success(self, mock_get):
        """Test successful metrics fetch"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "cpu_percent": 10.5,
            "memory_percent": 45.2,
            "disk_percent": 60.0,
        }
        mock_get.return_value = mock_response

        args = Mock()
        result = cli.cmd_metrics(args)
        assert result == 0

    @patch("requests.get")
    def test_cmd_metrics_failure(self, mock_get):
        """Test failed metrics fetch"""
        mock_get.side_effect = Exception("Connection error")
        args = Mock()
        result = cli.cmd_metrics(args)
        assert result == 1

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="log line 1\nlog line 2\n")
    def test_cmd_logs_all(self, mock_file, mock_exists):
        """Test viewing all logs"""
        mock_exists.return_value = True
        args = Mock(tail=None)
        result = cli.cmd_logs(args)
        assert result == 0

    @patch("pathlib.Path.exists")
    @patch(
        "builtins.open", new_callable=mock_open, read_data="log line 1\nlog line 2\nlog line 3\n"
    )
    def test_cmd_logs_tail(self, mock_file, mock_exists):
        """Test viewing last N log lines"""
        mock_exists.return_value = True
        args = Mock(tail=2)
        result = cli.cmd_logs(args)
        assert result == 0

    @patch("pathlib.Path.exists")
    def test_cmd_logs_file_not_found(self, mock_exists):
        """Test logs command when file doesn't exist"""
        mock_exists.return_value = False
        args = Mock(tail=None)
        result = cli.cmd_logs(args)
        assert result == 1


class TestTestingCommands:
    """Test testing commands"""

    @patch("autom8.cli.run_command")
    def test_cmd_test_success(self, mock_run):
        """Test successful test execution"""
        mock_run.return_value = (True, "All tests passed", "")
        args = Mock(coverage=False)
        result = cli.cmd_test(args)
        assert result == 0

    @patch("autom8.cli.run_command")
    def test_cmd_test_with_coverage(self, mock_run):
        """Test execution with coverage"""
        mock_run.return_value = (True, "All tests passed", "")
        args = Mock(coverage=True)
        result = cli.cmd_test(args)
        assert result == 0

    @patch("autom8.cli.run_command")
    def test_cmd_test_failure(self, mock_run):
        """Test failed test execution"""
        mock_run.return_value = (False, "", "Tests failed")
        args = Mock(coverage=False)
        result = cli.cmd_test(args)
        assert result == 1

    @patch("autom8.cli.run_command")
    def test_cmd_test_unit(self, mock_run):
        """Test unit tests execution"""
        mock_run.return_value = (True, "Unit tests passed", "")
        args = Mock()
        result = cli.cmd_test_unit(args)
        assert result == 0

    @patch("autom8.cli.run_command")
    def test_cmd_test_integration(self, mock_run):
        """Test integration tests execution"""
        mock_run.return_value = (True, "Integration tests passed", "")
        args = Mock()
        result = cli.cmd_test_integration(args)
        assert result == 0


class TestDevelopmentCommands:
    """Test development commands"""

    @patch("autom8.cli.run_command")
    def test_cmd_dev_setup_success(self, mock_run):
        """Test successful dev environment setup"""
        mock_run.return_value = (True, "", "")
        args = Mock()
        result = cli.cmd_dev_setup(args)
        assert result == 0

    @patch("autom8.cli.run_command")
    def test_cmd_dev_setup_failure(self, mock_run):
        """Test failed dev environment setup"""
        mock_run.return_value = (False, "", "Installation failed")
        args = Mock()
        result = cli.cmd_dev_setup(args)
        assert result == 1

    @patch("autom8.cli.run_command")
    def test_cmd_dev_lint_success(self, mock_run):
        """Test successful linting"""
        mock_run.return_value = (True, "No issues found", "")
        args = Mock()
        result = cli.cmd_dev_lint(args)
        assert result == 0

    @patch("autom8.cli.run_command")
    def test_cmd_dev_lint_failure(self, mock_run):
        """Test failed linting"""
        mock_run.return_value = (False, "", "Linting errors")
        args = Mock()
        result = cli.cmd_dev_lint(args)
        assert result == 1

    @patch("autom8.cli.run_command")
    def test_cmd_dev_format_success(self, mock_run):
        """Test successful code formatting"""
        mock_run.return_value = (True, "Code formatted", "")
        args = Mock()
        result = cli.cmd_dev_format(args)
        assert result == 0

    @patch("autom8.cli.run_command")
    def test_cmd_dev_format_failure(self, mock_run):
        """Test failed code formatting"""
        mock_run.return_value = (False, "", "Formatting failed")
        args = Mock()
        result = cli.cmd_dev_format(args)
        assert result == 1


class TestContactCommands:
    """Test contact management commands"""

    @patch("requests.get")
    def test_cmd_contacts_list_success(self, mock_get):
        """Test successful contact listing"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "contacts": [
                {"id": 1, "name": "John Doe", "phone": "0701234567"},
                {"id": 2, "name": "Jane Smith", "phone": "0702345678"},
            ]
        }
        mock_get.return_value = mock_response

        args = Mock()
        result = cli.cmd_contacts_list(args)
        assert result == 0

    @patch("requests.get")
    def test_cmd_contacts_list_empty(self, mock_get):
        """Test contact listing when empty"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"contacts": []}
        mock_get.return_value = mock_response

        args = Mock()
        result = cli.cmd_contacts_list(args)
        assert result == 0

    @patch("requests.get")
    def test_cmd_contacts_list_failure(self, mock_get):
        """Test failed contact listing"""
        mock_get.side_effect = Exception("Connection error")
        args = Mock()
        result = cli.cmd_contacts_list(args)
        assert result == 1

    @patch("requests.post")
    @patch("builtins.input", side_effect=["John Doe", "0701234567", "john@example.com"])
    def test_cmd_contacts_add_success(self, mock_input, mock_post):
        """Test successful contact addition"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 1}
        mock_post.return_value = mock_response

        args = Mock()
        result = cli.cmd_contacts_add(args)
        assert result == 0

    @patch("requests.post")
    @patch("builtins.input", side_effect=["John Doe", "0701234567", ""])
    def test_cmd_contacts_add_no_email(self, mock_input, mock_post):
        """Test contact addition without email"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 1}
        mock_post.return_value = mock_response

        args = Mock()
        result = cli.cmd_contacts_add(args)
        assert result == 0

    @patch("builtins.input", side_effect=KeyboardInterrupt)
    def test_cmd_contacts_add_cancelled(self, mock_input):
        """Test contact addition cancellation"""
        args = Mock()
        result = cli.cmd_contacts_add(args)
        assert result == 0

    @patch("requests.post")
    @patch("builtins.input", side_effect=["John Doe", "0701234567", ""])
    def test_cmd_contacts_add_failure(self, mock_input, mock_post):
        """Test failed contact addition"""
        mock_post.side_effect = Exception("Connection error")
        args = Mock()
        result = cli.cmd_contacts_add(args)
        assert result == 1

    @patch("requests.delete")
    def test_cmd_contacts_delete_success(self, mock_delete):
        """Test successful contact deletion"""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response

        args = Mock(id=1)
        result = cli.cmd_contacts_delete(args)
        assert result == 0

    def test_cmd_contacts_delete_no_id(self):
        """Test contact deletion without ID"""
        args = Mock(id=None)
        result = cli.cmd_contacts_delete(args)
        assert result == 1

    @patch("requests.delete")
    def test_cmd_contacts_delete_failure(self, mock_delete):
        """Test failed contact deletion"""
        mock_delete.side_effect = Exception("Connection error")
        args = Mock(id=1)
        result = cli.cmd_contacts_delete(args)
        assert result == 1

    @patch("requests.get")
    def test_cmd_contacts_search_by_name(self, mock_get):
        """Test successful search by name"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "contacts": [
                {"id": 1, "name": "Bitter", "phone": "0701234567", "email": "bitter@example.com"},
                {"id": 2, "name": "John Bitter", "phone": "0702345678", "email": "john.bitter@example.com"},
                {"id": 3, "name": "Jane Smith", "phone": "0703456789", "email": "jane@example.com"},
            ]
        }
        mock_get.return_value = mock_response

        args = Mock()
        args.name = "Bitter"
        args.phone = None
        args.email = None
        result = cli.cmd_contacts_search(args)
        assert result == 0
        mock_get.assert_called_once_with("http://localhost:5000/api/v1/contacts", timeout=5)

    @patch("requests.get")
    def test_cmd_contacts_search_by_phone(self, mock_get):
        """Test successful search by phone"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "contacts": [
                {"id": 1, "name": "John Doe", "phone": "0701234567", "email": "john@example.com"},
                {"id": 2, "name": "Jane Smith", "phone": "0702345678", "email": "jane@example.com"},
            ]
        }
        mock_get.return_value = mock_response

        args = Mock()
        args.name = None
        args.phone = "0701234567"
        args.email = None
        result = cli.cmd_contacts_search(args)
        assert result == 0

    @patch("requests.get")
    def test_cmd_contacts_search_by_email(self, mock_get):
        """Test successful search by email"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "contacts": [
                {"id": 1, "name": "John Doe", "phone": "0701234567", "email": "john@example.com"},
                {"id": 2, "name": "Jane Smith", "phone": "0702345678", "email": "jane@example.com"},
            ]
        }
        mock_get.return_value = mock_response

        args = Mock()
        args.name = None
        args.phone = None
        args.email = "john@example.com"
        result = cli.cmd_contacts_search(args)
        assert result == 0

    @patch("requests.get")
    def test_cmd_contacts_search_multiple_parameters(self, mock_get):
        """Test search with multiple parameters"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "contacts": [
                {"id": 1, "name": "John Doe", "phone": "0701234567", "email": "john@example.com"},
                {"id": 2, "name": "Jane Smith", "phone": "0702345678", "email": "jane@example.com"},
                {"id": 3, "name": "Bitter", "phone": "0703456789", "email": "bitter@example.com"},
            ]
        }
        mock_get.return_value = mock_response

        args = Mock()
        args.name = "John"
        args.phone = "070"
        args.email = None
        result = cli.cmd_contacts_search(args)
        assert result == 0

    @patch("requests.get")
    def test_cmd_contacts_search_no_results(self, mock_get):
        """Test search with no matching contacts"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "contacts": [
                {"id": 1, "name": "John Doe", "phone": "0701234567", "email": "john@example.com"},
                {"id": 2, "name": "Jane Smith", "phone": "0702345678", "email": "jane@example.com"},
            ]
        }
        mock_get.return_value = mock_response

        args = Mock()
        args.name = "NonExistent"
        args.phone = None
        args.email = None
        result = cli.cmd_contacts_search(args)
        assert result == 0

    def test_cmd_contacts_search_no_parameters(self):
        """Test search with no parameters"""
        args = Mock()
        args.name = None
        args.phone = None
        args.email = None
        result = cli.cmd_contacts_search(args)
        assert result == 1

    @patch("requests.get")
    def test_cmd_contacts_search_api_failure(self, mock_get):
        """Test search with API failure"""
        mock_get.side_effect = Exception("Connection error")
        args = Mock()
        args.name = "Bitter"
        args.phone = None
        args.email = None
        result = cli.cmd_contacts_search(args)
        assert result == 1

    @patch("requests.get")
    def test_cmd_contacts_search_api_error_response(self, mock_get):
        """Test search with API error response"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        args = Mock()
        args.name = "Bitter"
        args.phone = None
        args.email = None
        result = cli.cmd_contacts_search(args)
        assert result == 1


class TestMainFunction:
    """Test main CLI function"""

    @patch("sys.argv", ["autom8", "--version"])
    def test_main_version(self):
        """Test version flag"""
        with pytest.raises(SystemExit) as exc_info:
            cli.main()
        assert exc_info.value.code == 0

    @patch("sys.argv", ["autom8"])
    def test_main_no_command(self):
        """Test main with no command"""
        result = cli.main()
        assert result == 0

    @patch("sys.argv", ["autom8", "health"])
    @patch("autom8.cli.cmd_health")
    def test_main_with_command(self, mock_cmd):
        """Test main with valid command"""
        mock_cmd.return_value = 0
        result = cli.main()
        assert result == 0

    @patch("sys.argv", ["autom8", "api", "start"])
    @patch("autom8.cli.cmd_api_start")
    def test_main_keyboard_interrupt(self, mock_cmd):
        """Test main with keyboard interrupt"""
        mock_cmd.side_effect = KeyboardInterrupt
        result = cli.main()
        assert result == 0

    @patch("sys.argv", ["autom8", "api", "start"])
    @patch("autom8.cli.cmd_api_start")
    def test_main_exception(self, mock_cmd):
        """Test main with unexpected exception"""
        mock_cmd.side_effect = Exception("Unexpected error")
        result = cli.main()
        assert result == 1


class TestPlatformSpecific:
    """Test platform-specific behavior"""

    @patch("sys.platform", "win32")
    @patch("autom8.cli.run_command")
    def test_api_stop_windows(self, mock_run):
        """Test API stop on Windows"""
        mock_run.return_value = (True, "", "")
        args = Mock()
        cli.cmd_api_stop(args)
        call_args = mock_run.call_args[0][0]
        assert "taskkill" in call_args

    @patch("sys.platform", "linux")
    @patch("autom8.cli.run_command")
    def test_api_stop_linux(self, mock_run):
        """Test API stop on Linux"""
        mock_run.return_value = (True, "", "")
        args = Mock()
        cli.cmd_api_stop(args)
        call_args = mock_run.call_args[0][0]
        assert "pkill" in call_args
