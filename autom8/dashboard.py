"""
dashboard.py - Real-time Monitoring Dashboard
Displays system health, metrics, recent logs
"""

import time
import os
from datetime import datetime
from autom8.models import get_session, TaskLog
from autom8.metrics import get_all_metrics
from autom8.scheduler import get_scheduled_jobs


def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")  # nosec B605


def get_status_emoji(value, warning_threshold, critical_threshold):
    if value > critical_threshold:
        return "[!]"
    elif value > warning_threshold:
        return "[*]"
    else:
        return "[OK]"


def _print_header():
    clear_screen()
    print("=" * 80)
    print(" " * 25 + "AUTOM8 MONITORING DASHBOARD")
    print("=" * 80)
    print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()


def _print_system_metrics(metrics):
    print("System Resources")
    print("-" * 80)

    cpu_percent = metrics["system"]["cpu"]["percent"]
    mem_percent = metrics["system"]["memory"]["percent"]
    disk_percent = metrics["system"]["disk"]["percent"]
    mem_used = metrics["system"]["memory"]["used_mb"]
    mem_total = metrics["system"]["memory"]["total_mb"]
    disk_used = metrics["system"]["disk"]["used_gb"]
    disk_total = metrics["system"]["disk"]["total_gb"]

    print(f"  {get_status_emoji(cpu_percent, 70, 90)} CPU:    {cpu_percent:.1f}% used")
    print(
        f"  {get_status_emoji(mem_percent, 70, 90)} Memory: {mem_percent:.1f}% used "
        f"({mem_used} MB / {mem_total} MB)"
    )
    print(
        f"  {get_status_emoji(disk_percent, 70, 90)} Disk:   {disk_percent:.1f}% used "
        f"({disk_used} GB / {disk_total} GB)"
    )


def _print_task_stats(metrics):
    print("\nTask Execution Statistics")
    print("-" * 80)

    task_stats = metrics["tasks"]
    print(f"  Total Executions: {task_stats['total_executions']}")
    print(f"  Completed: {task_stats['completed']}")
    print(f"  Failed: {task_stats['failed']}")
    print(f"  Running: {task_stats['running']}")
    print(f"  Success Rate: {task_stats['success_rate']:.1f}%")


def _print_scheduled_jobs():
    print("\nScheduled Jobs")
    print("-" * 80)

    jobs = get_scheduled_jobs()
    if jobs:
        for job in jobs[:5]:  # Show first 5
            next_run = job.get("next_run_time", "N/A")
            print(f"  - {job['name']}")
            print(f"    Next run: {next_run}")
    else:
        print("  No jobs scheduled")


def _print_recent_logs():
    print("\n Recent Task Executions (Last 5)")
    print("-" * 80)

    session = get_session()
    try:
        recent_logs = (
            session.query(TaskLog).order_by(TaskLog.started_at.desc()).limit(5).all()
        )

        for log in recent_logs:
            status_icon = {"completed": "[OK]", "failed": "[!]", "running": "[*]"}.get(
                log.status, "[?]"
            )

            duration = ""
            if log.completed_at and log.started_at:
                delta = log.completed_at - log.started_at
                duration = f" ({delta.total_seconds():.1f}s)"

            print(f"  {status_icon} {log.task_type} - {log.status} {duration}")
            print(f"     {log.started_at.strftime('%Y-%m-%d %H:%M:%S')}")

            if log.error_message:
                print(f"     Error: {log.error_message[:60]}...")

    finally:
        session.close()


def _print_db_stats(metrics):
    print("\nDatabase Statistics")
    print("-" * 80)
    db_stats = metrics["database"]
    print(f"  Contacts: {db_stats['contacts']}")
    print(f"  Task Logs: {db_stats['task_logs']}")


def display_dashboard():
    """Display real-time monitoring dashboard."""
    try:
        while True:
            _print_header()

            # Fetch metrics
            try:
                metrics = get_all_metrics()
                _print_system_metrics(metrics)
                _print_task_stats(metrics)
                _print_scheduled_jobs()
                _print_recent_logs()
                _print_db_stats(metrics)

            except Exception as e:
                print(f"Error fetching metrics: {e}")

            print("\n" + "=" * 80)
            print("Press Ctrl+C to exit | Refreshes every 10 seconds")
            print("=" * 80)

            time.sleep(10)

    except KeyboardInterrupt:
        print("\n\nDashboard stopped")


if __name__ == "__main__":
    display_dashboard()
