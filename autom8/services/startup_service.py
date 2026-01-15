# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""
startup_service.py - System Startup Utilities
Handles reconciliation of interrupted tasks and other boot-time checks.
"""

from datetime import datetime
from autom8.core import log
from autom8.models import TaskLog, get_session


def reconcile_zombie_tasks():
    """
    Finds all TaskLog entries with status 'running' and marks them as 'interrupted'.
    This should be run once on system startup.
    """
    session = get_session()
    try:
        zombies = session.query(TaskLog).filter(TaskLog.status == "running").all()

        if not zombies:
            log.info("Startup reconciliation: No zombie tasks found.")
            return

        count = len(zombies)
        log.warning(f"Startup reconciliation: Found {count} zombie tasks. Marking as interrupted.")

        for task in zombies:
            task.status = "interrupted"
            task.completed_at = datetime.now()
            task.error_message = "System shutdown or interruption detected."

        session.commit()
        log.info(f"Startup reconciliation: Successfully recovered {count} tasks.")

    except Exception as e:
        log.error(f"Startup reconciliation failed: {e}")
    finally:
        session.close()
