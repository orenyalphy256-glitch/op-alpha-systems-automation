"""
test_scheduler.py - Test scheduler functionality
Run: python -m autom8.test_scheduler
"""

import time
from datetime import datetime, timedelta
from autom8.scheduler import (
    init_scheduler,
    start_scheduler,
    stop_scheduler,
    schedule_backup_job,
    schedule_cleanup_job,
    get_scheduled_jobs,
    run_job_now,
)
from autom8.models import get_session, TaskLog
from autom8.core import log


def test_scheduler():
    print("=" * 60)
    print("SCHEDULER TESTING")
    print("=" * 60)

    # Test 1: Initialize
    print("\nTest 1: Initializing scheduler...")
    try:
        init_scheduler()
        print("Scheduler initialized successfully")
    except Exception as e:
        print(f"Failed: {e}")
        return

    # Test 2: Schedule jobs
    print("\nTest 2: Scheduling jobs...")
    try:
        schedule_backup_job()
        schedule_cleanup_job()
        print("Jobs scheduled successfully")
    except Exception as e:
        print(f"Failed: {e}")
        return

    # Test 3: List jobs
    print("\nTest 3: Listing scheduled jobs...")
    jobs = get_scheduled_jobs()
    print(f"Found {len(jobs)} jobs:")
    for job in jobs:
        print(f"  - {job['name']}")
        print(f"    - ID: {job['id']}")
        print(f"    - Trigger: {job['trigger']}")
        print(f"    - Next run: {job['next_run_time']}")
        print()

    # Test 4: Start scheduler
    print("\nTest 4: Starting scheduler...")
    try:
        start_scheduler()
        print("Scheduler started successfully")
    except Exception as e:
        print(f"Failed: {e}")
        return

    # Test 5: Manual trigger
    print("\nTest 5: Manually triggering backup job...")
    try:
        run_job_now("backup_job")
        print("Backup job triggered successfully")
        time.sleep(2)  # Wait for task execution
    except Exception as e:
        print(f"Failed: {e}")

    # Test 6: Check database logs
    print("\nTest 6: Checking database logs...")
    session = get_session()
    try:
        logs = session.query(TaskLog).order_by(TaskLog.started_at.desc()).limit(5).all()
        print(f"Found {len(logs)} logs:")
        for log_entry in logs:
            print(f"  - {log_entry.task_type} ({log_entry.status})")
            print(f"    - Started at: {log_entry.started_at}")
            print(f"    - Completed at: {log_entry.completed_at}")
            if log_entry.error_message:
                print(f"    - Error message: {log_entry.error_message}")
            print()
    finally:
        session.close()

    # Test 7: Stop scheduler
    print("\nTest 7: Stopping scheduler...")
    try:
        stop_scheduler()
        print("Scheduler stopped successfully")
    except Exception as e:
        print(f"Failed: {e}")

    print("\n" + "=" * 60)
    print("SCHEDULER TESTING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_scheduler()
