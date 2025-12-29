# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""

run_scheduler.py - Run the scheduler
Runs scheduler tasks in background

Usage: python run_scheduler.py # Run forever
    python run_scheduler.py --once # Run once
"""

import signal
import sys
import time

from autom8.core import log
from autom8.scheduler import (
    get_scheduled_jobs,
    init_scheduler,
    schedule_all_jobs,
    start_scheduler,
    stop_scheduler,
)

# Global flag for graceful shutdown
shutdown_requested = False


def signal_handler(sig, frame):
    global shutdown_requested
    log.info("Shutdown signal received (Ctrl+C). Stopping scheduler...")
    shutdown_requested = True


def main():
    global shutdown_requested

    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    # Check for --once flag (test mode)
    test_mode = "--once" in sys.argv

    print("=" * 60)
    print("AUTOM8 SCHEDULER SERVICE")
    print("=" * 60)

    # Initialize scheduler
    log.info("Initializing scheduler...")
    init_scheduler()

    # Schedule all jobs
    log.info("Scheduling jobs")
    schedule_all_jobs()

    # Display scheduled jobs
    jobs = get_scheduled_jobs()
    print(f"\n Scheduled Jobs ({len(jobs)}):")
    for job in jobs:
        print(f"  - {job['name']} (ID: {job['id']})")
        print(f"    -Next run: {job['next_run_time']}")
        print(f"    -Trigger: {job['trigger']}")
        print()

    # Start scheduler
    log.info("Starting scheduler...")
    start_scheduler()
    print("Scheduler started. Press Ctrl+C to stop...")
    print("Monitoring: Check logs/system.log for job execution logs")
    print(" Press Ctrl+C to stop\n")

    if test_mode:
        print("Running in test mode: Press Ctrl+C to stop...")
        time.sleep(30)
        shutdown_requested = True
    else:
        # Run until interrupted
        try:
            while not shutdown_requested:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    # Graceful shutdown
    print("\nStopping scheduler...")
    log.info("Stopping scheduler (graceful shutdown)...")
    stop_scheduler(wait=True)
    print("Scheduler stopped successfully.")
    log.info("Scheduler service exited")


if __name__ == "__main__":
    main()
