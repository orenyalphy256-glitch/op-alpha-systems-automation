# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""
execution_service.py - Task Execution Service
Centralizes task execution, logging, and alert triggering.
Implements Double-Fault protection with Optimized Session Handling.
"""

import json
from datetime import datetime

from autom8.alerts import alert_task_failure
from autom8.core import LOGS_DIR, log
from autom8.models import TaskLog, get_session
from autom8.tasks import run_task


class ExecutionService:
    """
    Guarantees:
    - TaskLog lifecycle managed
    - Failures never masked
    - Alerts sent even if DB is down
    - Optimized performance via session reuse
    """

    @staticmethod
    def execute_task(task_type, task_name=None, **kwargs):
        """Executes a task and manages its lifecycle."""
        start_time = datetime.now()

        # 1. Initialize Log
        session, task_log_id = ExecutionService._initialize_log(task_type, task_name, start_time)

        # 2. Execute Task
        result = ExecutionService._run_task(task_type, task_name)

        # 3. Finalize Task Log
        status = "completed" if result.get("status") == "success" else "failed"
        ExecutionService._finalize_log(session, task_log_id, task_type, status, result)

        # 4. Trigger Alerts (Independent of DB)
        if status == "failed":
            alert_task_failure(task_type, result.get("error", "Unknown error"))

        return result

    @staticmethod
    def _initialize_log(task_type, task_name, start_time):
        """Initialize DB log entry for the task."""
        session = None
        task_log_id = None
        try:
            session = get_session()
            task_log = TaskLog(
                task_type=task_type,
                task_name=task_name or task_type,
                status="running",
                started_at=start_time,
            )
            session.add(task_log)
            session.commit()
            session.refresh(task_log)
            task_log_id = task_log.id
            log.info(f"Task {task_type} started (Log ID: {task_log_id})")
        except Exception as e:
            log.error(f"Double-Fault: DB failed during task init for {task_type}: {e}")
            ExecutionService._log_to_disk(task_type, "running", {"error": "DB_DOWN", "msg": str(e)})
        return session, task_log_id

    @staticmethod
    def _run_task(task_type, task_name):
        """Execute the actual task logic."""
        result = {"status": "failed", "error": "Unknown error"}
        try:
            result = run_task(task_type, name=task_name)
        except Exception as e:
            result = {"status": "failed", "error": str(e)}
            log.error(f"Critical task execution error for {task_type}: {e}")
        return result

    @staticmethod
    def _finalize_log(session, task_log_id, task_type, status, result):
        """Finalize the DB log entry with the result."""
        end_time = datetime.now()
        try:
            if session and task_log_id:
                task_log = session.query(TaskLog).get(task_log_id)
                if task_log:
                    task_log.status = status
                    task_log.completed_at = end_time
                    if status == "completed":
                        task_log.result_data = str(result)[:500]
                    else:
                        task_log.error_message = str(result.get("error", "Unknown"))[:500]
                    session.commit()
                    log.info(f"Task {task_type} finished: {status} (Log ID: {task_log_id})")
                else:
                    raise RuntimeError("Log record not found")
            else:
                raise RuntimeError("No active session or log ID")
        except Exception as e:
            log.error(f"Double-Fault: DB failed during task finalize for {task_type}: {e}")
            ExecutionService._log_to_disk(task_type, status, result)
        finally:
            if session:
                session.close()

    @staticmethod
    def _log_to_disk(task_type, status, data):
        """Fallback logging to disk when DB is down."""
        fallback_file = LOGS_DIR / "task_execution_fallback.jsonl"
        entry = {
            "timestamp": datetime.now().isoformat(),
            "task_type": task_type,
            "status": status,
            "data": data,
        }
        try:
            with open(fallback_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
            log.warning(f"Fallback log written to disk for {task_type}")
        except Exception as e:
            log.critical(f"TRIPLE-FAULT: Could not even log to disk! {e}")
