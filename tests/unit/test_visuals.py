"""
Unit tests for visual/CLI modules: dashboard, monitor_scheduler, and analyze_logs.
Uses mocking to test infinite loops and print statements without hanging.
"""

import pytest
import json
import os
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime, timedelta

from autom8.dashboard import (
    clear_screen, 
    get_status_emoji, 
    display_dashboard
)
from autom8.monitor_scheduler import (
    format_timedelta, 
    monitor_dashboard
)
from autom8.analyze_logs import (
    parse_json_logs, 
    analyze_log_levels, 
    analyze_errors, 
    analyze_modules, 
    generate_report
)

# ============================================================================
# Dashboard Tests
# ============================================================================

def test_clear_screen():
    with patch("os.system") as mock_system:
        clear_screen()
        mock_system.assert_called()

def test_get_status_emoji():
    assert get_status_emoji(95, 70, 90) == "[!]"
    assert get_status_emoji(80, 70, 90) == "[*]"
    assert get_status_emoji(50, 70, 90) == "[OK]"

@patch("autom8.dashboard.get_all_metrics")
@patch("autom8.dashboard.get_scheduled_jobs")
@patch("autom8.dashboard.get_session")
@patch("autom8.dashboard.time.sleep")
def test_display_dashboard(mock_sleep, mock_session, mock_jobs, mock_metrics):
    """Test dashboard display loop (run once then exit via exception)."""
    # Mock Metrics
    mock_metrics.return_value = {
        "system": {
            "cpu": {"percent": 10},
            "memory": {"percent": 20, "used_mb": 100, "total_mb": 500},
            "disk": {"percent": 30, "used_gb": 10, "total_gb": 100}
        },
        "tasks": {
            "total_executions": 10,
            "completed": 8,
            "failed": 2,
            "running": 0,
            "success_rate": 80.0
        },
        "database": {"contacts": 1, "task_logs": 5}
    }
    
    # Mock Jobs
    mock_jobs.return_value = [{"name": "Test Job", "next_run_time": "2025-01-01"}]
    
    # Mock Session and Logs
    mock_db = MagicMock()
    mock_log = MagicMock()
    mock_log.status = "completed"
    mock_log.task_type = "backup"
    mock_log.started_at = datetime.now()
    mock_log.completed_at = datetime.now()
    mock_log.error_message = None
    
    # Setup query chain
    mock_db.query.return_value.order_by.return_value.limit.return_value.all.return_value = [mock_log]
    mock_session.return_value = mock_db
    
    # Force loop break after one iteration using side_effect
    mock_sleep.side_effect = KeyboardInterrupt
    
    # Run
    display_dashboard()
    
    # Assertions
    mock_metrics.assert_called()
    mock_jobs.assert_called()


# ============================================================================
# Monitor Scheduler Tests
# ============================================================================

def test_format_timedelta():
    assert format_timedelta(timedelta(seconds=45)) == "45s"
    assert format_timedelta(timedelta(minutes=2, seconds=30)) == "2m 30s"
    assert format_timedelta(timedelta(hours=2, minutes=15)) == "2h 15m"
    assert format_timedelta(None) == "N/A"

@patch("autom8.monitor_scheduler.get_scheduled_jobs")
@patch("autom8.monitor_scheduler.get_session")
@patch("autom8.monitor_scheduler.time.sleep")
def test_monitor_dashboard(mock_sleep, mock_session, mock_jobs):
    """Test monitor dashboard loop."""
    # Mock Jobs
    # One job with ISO format time, one without
    mock_jobs.return_value = [
        {"name": "Job 1", "next_run_time": (datetime.now() + timedelta(hours=1)).isoformat()},
        {"name": "Job 2", "next_run_time": None}
    ]
    
    # Mock Session
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    mock_db.query.return_value.order_by.return_value.limit.return_value.all.return_value = []
    # FIX: Mock count() to return 0 for statistics
    mock_db.query.return_value.count.return_value = 0
    mock_db.query.return_value.filter.return_value.count.return_value = 0
    
    # Break loop
    mock_sleep.side_effect = KeyboardInterrupt
    
    # Run
    monitor_dashboard()
    
    # Should handle the loop gracefully
    mock_sleep.assert_called()


# ============================================================================
# Analyze Logs Tests
# ============================================================================

def test_parse_json_logs_no_file():
    with patch("pathlib.Path.exists", return_value=False):
        logs = parse_json_logs()
        assert logs == []

def test_parse_json_logs_valid(tmp_path):
    # Create dummy log file
    log_file = tmp_path / "test_logs.json"
    
    log_data = [
        # Recent entry
        {
            "timestamp": datetime.now().isoformat() + "Z",
            "level": "INFO", 
            "message": "Test", 
            "module": "test",
            "function": "test",
            "line": 1
        },
        # Old entry
        {
            "timestamp": (datetime.now() - timedelta(hours=48)).isoformat() + "Z",
            "level": "INFO",
            "message": "Old",
            "module": "test", 
             "function": "test",
            "line": 2
        },
         # Invalid JSON
        "INVALID JSON LINE"
    ]
    
    with open(log_file, "w") as f:
        for entry in log_data:
            if isinstance(entry, dict):
                f.write(json.dumps(entry) + "\n")
            else:
                f.write(entry + "\n")
                
    # Mock the LOGS_DIR to point to our temp dir
    with patch("autom8.analyze_logs.LOGS_DIR", tmp_path):
        entries = parse_json_logs("test_logs.json", hours=24)
        
        # Should only get the recent entry, ignore old and invalid
        assert len(entries) == 1
        assert entries[0]["message"] == "Test"

def test_log_analysis_functions(capsys):
    entries = [
        {"level": "INFO", "module": "mod1", "message": "msg1"},
        {"level": "ERROR", "module": "mod2", "message": "msg2", "timestamp": "2025-01-01", "function": "fn", "line": 1},
        {"level": "INFO", "module": "mod1", "message": "msg3"}
    ]
    
    # Level Analysis
    levels = analyze_log_levels(entries)
    assert levels["INFO"] == 2
    assert levels["ERROR"] == 1
    
    # Module Analysis
    parse_out = capsys.readouterr() # clean buffer
    analyze_modules(entries)
    captured = capsys.readouterr()
    assert "mod1" in captured.out
    
    # Error Analysis
    analyze_errors(entries)
    captured = capsys.readouterr()
    assert "msg2" in captured.out

@patch("autom8.analyze_logs.parse_json_logs")
def test_generate_report(mock_parse):
    mock_parse.return_value = [{"level": "INFO", "module": "test", "message": "test"}]
    
    generate_report(24)
    # Just asserting it runs without error
    mock_parse.assert_called_with(hours=24)
    
    # Test empty
    mock_parse.return_value = []
    generate_report(24)
