import json
from unittest.mock import MagicMock, patch

from autom8.alerts import alert_system_issue, alert_task_failure, send_email_alert
from autom8.core import ContextLogger, JSONFormatter, load_json, save_json, setup_logging
from autom8.metrics import (
    get_all_metrics,
    get_database_metrics,
    get_system_metrics,
    get_task_metrics,
)

# ============================================================================
# Core Tests
# ============================================================================


def test_json_operations(tmp_path):
    f = tmp_path / "test.json"
    data = {"key": "val"}

    # Save
    assert save_json(f, data) is True
    assert f.exists()

    # Load
    loaded = load_json(f)
    assert loaded == data

    # Load non-existent
    assert load_json(tmp_path / "missing.json") == {}

    # Load invalid
    f.write_text("invalid json")
    assert load_json(f) == {}


def test_json_formatter():
    formatter = JSONFormatter()
    record = MagicMock()
    record.levelname = "INFO"
    record.name = "test"
    record.getMessage.return_value = "msg"
    record.funcName = "fn"
    record.lineno = 10
    record.exc_info = None

    output = formatter.format(record)
    data = json.loads(output)
    assert data["message"] == "msg"
    assert "timestamp" in data


def test_context_logger():
    mock_logger = MagicMock()
    with patch("logging.getLogger", return_value=mock_logger):
        cl = ContextLogger()
        cl.info("Test", user="admin")

        mock_logger.log.assert_called()
        args, kwargs = mock_logger.log.call_args
        assert kwargs["extra"]["extra_data"] == {"user": "admin"}


def test_setup_logging(tmp_path):
    with patch("autom8.core.LOGS_DIR", tmp_path):
        logger = setup_logging("test_app", console_output=False, json_logs=True, text_logs=True)
        assert logger.handlers
        assert (tmp_path / "test_app_json.log").exists()


# ============================================================================
# Metrics Tests
# ============================================================================


def test_system_metrics():
    metrics = get_system_metrics()
    assert metrics is not None
    assert "cpu" in metrics
    assert "memory" in metrics
    assert "disk" in metrics


@patch("autom8.metrics.get_session")
def test_task_metrics(mock_session):
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    mock_db.query.return_value.count.return_value = 10

    metrics = get_task_metrics()
    assert metrics["total_executions"] == 10


@patch("autom8.metrics.get_session")
def test_database_metrics(mock_session):
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    mock_db.query.return_value.count.return_value = 5

    metrics = get_database_metrics()
    assert metrics["contacts"] == 5


def test_get_all_metrics():
    with patch("autom8.metrics.get_system_metrics") as mock_sys:
        mock_sys.return_value = {}
        with patch("autom8.metrics.get_task_metrics") as mock_task:
            mock_task.return_value = {}
            with patch("autom8.metrics.get_database_metrics") as mock_db:
                mock_db.return_value = {}

                all_m = get_all_metrics()
                assert "system" in all_m


# ============================================================================
# Alerts Tests
# ============================================================================


@patch("smtplib.SMTP")
def test_send_email_alert(mock_smtp):
    with patch("autom8.alerts.SMTP_USERNAME", "user"), patch("autom8.alerts.SMTP_PASSWORD", "pass"):

        res = send_email_alert("Subj", "Body")
        assert res is True
        mock_smtp.return_value.__enter__.return_value.sendmail.assert_called()


def test_send_email_no_creds():
    with patch("autom8.alerts.SMTP_USERNAME", ""):
        res = send_email_alert("Subj", "Body")
        assert res is False


@patch("autom8.alerts.send_email_alert")
def test_alert_wrappers(mock_send):
    alert_task_failure("backup", "error")
    mock_send.assert_called()

    alert_system_issue("disk", "full")
    mock_send.assert_called()
