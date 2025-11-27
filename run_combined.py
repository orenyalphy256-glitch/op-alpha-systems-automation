"""
run_combined.py - Run Flask API + Scheduler in one process
Usage: python run_combined.py
"""
import os
import signal
import sys

# Import core FIRST (no dependencies)
from autom8.core import log

# Import models (depends on core)
from autom8.models import init_db

# Import scheduler (depends on models + core)
from autom8.scheduler import (
    init_scheduler,
    start_scheduler,
    stop_scheduler,
    schedule_all_jobs,
    get_scheduled_jobs
)

# Import API (depends on everything)
from autom8.api import app

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

    # Initialize database
    print("\n Initializing database...")
    init_db()
    print(" Database ready")

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
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('API_DEBUG', 'False').lower() == 'true'

    # Start Flask API
    print(f"\n Starting Flask API on {host}:{port}")
    print(f"   Debug mode: {debug}")
    print(f"   API: http://{host}:{port}/")
    print(f"   Health: http://{host}:{port}/api/v1/health")
    print("\n Press Ctrl+C to stop both services\n")

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
