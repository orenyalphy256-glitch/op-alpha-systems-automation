"""
test_monitoring.py - Test monitoring and logging features
"""

from autom8.metrics import get_all_metrics
from autom8.alerts import send_email_alert
from autom8.core import log, ContextLogger
import sys

sys.stdout.reconfigure(encoding="utf-8")


def test_logging_levels():
    """Test different log levels."""
    print("\n[TEST 1] Testing log levels...")

    log.debug("This is a DEBUG message (development only)")
    log.info("This is an INFO message (normal operation)")
    log.warning("This is a WARNING message (something unexpected)")
    log.error("This is an ERROR message (something broke)")
    log.critical("This is a CRITICAL message (system failure)")

    print("✅ Check 99-Logs/ for log files")


def test_structured_logging():
    """Test structured logging with context."""
    print("\n[TEST 2] Testing structured logging...")

    context_log = ContextLogger("test")

    context_log.info("User login event", user="alphonce", ip="192.168.1.100", duration_ms=234)

    context_log.error(
        "Database connection failed", database="contacts", error_code=1045, retry_count=3
    )

    print("✅ Check autom8_json.log for structured entries")


def test_metrics():
    """Test metrics collection."""
    print("\n[TEST 3] Testing metrics collection...")

    metrics = get_all_metrics()

    print("\nSystem Metrics:")
    print(f"  CPU: {metrics['system']['cpu']['percent']}%")
    print(f"  Memory: {metrics['system']['memory']['percent']}%")
    print(f"  Disk: {metrics['system']['disk']['percent']}%")

    print("\nTask Metrics:")
    print(f"  Total: {metrics['tasks']['total_executions']}")
    print(f"  Success Rate: {metrics['tasks']['success_rate']}%")

    print("✅ Metrics collection working")


def test_alerting():
    """Test email alerting (if configured)."""
    print("\n[TEST 4] Testing email alerts...")

    import os

    if not os.getenv("SMTP_USERNAME"):
        print("⚠️  Email not configured - skipping alert test")
        print("   Set SMTP_USERNAME and SMTP_PASSWORD in .env to test")
        return

    result = send_email_alert(
        "Test Alert", "<p>This is a test alert from Autom8 monitoring system</p>"
    )

    if result:
        print("✅ Alert email sent successfully")
    else:
        print("❌ Alert email failed")


def main():
    """Run all monitoring tests."""
    print("=" * 60)
    print("MONITORING & LOGGING TESTS")
    print("=" * 60)

    test_logging_levels()
    test_structured_logging()
    test_metrics()
    test_alerting()

    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 60)
    print("\nCheck the following:")
    print("  1. 99-Logs/autom8_json.log (JSON structured logs)")
    print("  2. 99-Logs/autom8_text.log (Human-readable logs)")
    print("  3. 99-Logs/autom8_errors.log (Errors only)")
    print("  4. Console output above")


if __name__ == "__main__":
    main()
