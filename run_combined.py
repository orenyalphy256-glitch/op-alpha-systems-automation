"""
run_combined.py - Run Flask API + Scheduler in one process
Usage: python run_combined.py
"""
import os
import signal
import sys
from threading import Thread
from autom8.api import app
from autom8.scheduler import (
    init_scheduler,
    start_scheduler,
    stop_scheduler,
    schedule_all_jobs,
    get_scheduled_jobs
)
from autom8.core import log

# Global flag for graceful shutdown
shutdown_requested = False

def signal_handler(sig, frame):
    global shutdown_requested
    log.info("Shutdown signal received (Ctrl+C). Stopping scheduler...")
    shutdown_requested = True
    sys.exit(0)

def main():
    """Run combined API & Scheduler in one process."""

    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)

    print("=" * 60)
    print("AUTOM8 COMBINED SERVICE")
    print("API + SCHEDULER")
    print("=" * 60)

    # Initialize scheduler
    print("\nInitializing scheduler...")
    init_scheduler()
    schedule_all_jobs()

    # Display scheduled jobs
    jobs = get_scheduled_jobs()
    print(f"Scheduled {len(jobs)} jobs:")
    for job in jobs:
        print(f"  - {job['name']} -> Next run: {job['next_run_time']}")

    # Start scheduler
    print("\nStarting scheduler...")
    start_scheduler()
    print("Scheduler running")

    # Configuration
    host = os.getenv('API_HOST', '127.0.0.1')
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('API_DEBUG', 'False').lower() == 'true'

    # Start Flask API
    print(f"\nStarting Flask API on {host}:{port}")
    print(f"    Debug mode: {debug}")
    print(f"    Access API at: http://{host}:{port}/")
    print(f"    Scheduler status: http://{host}:{port}/api/v1/scheduler/status")
    print(f"    Task logs: http://{host}:{port}/api/v1/tasklogs")
    print("\nPress Ctrl+C to stop both services\n")

    log.info("Combined service started (API + Scheduler)")

    try:
        # Run Flask (blocks until stopped)
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=False
        )
    except KeyboardInterrupt:
        pass
    finally:
        # Shutdown scheduler gracefully
        print("\nStopping scheduler...")
        stop_scheduler(wait=True)
        print("Services stopped")
        log.info("Combined service exited")

if __name__ == "__main__":
    main()
