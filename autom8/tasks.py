# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""

tasks.py - Task Management with Design Patterns
Implements: Factory Pattern, Abstract Base Class (ABC)
"""

from abc import ABC, abstractmethod
from datetime import datetime

from autom8.core import DATA_DIR, log, save_json


# Abstract Base Class - Task Interface
class Task(ABC):
    """
    Abstract base class defining the Task interface
    All task types must inherit from this and implement execute().
    """

    def __init__(self, name=None):
        """
        Initialize task with optional name and timestamp.
        Args:
            name (str): Human-readable task name
        """
        self.name = name or self.__class__.__name__
        self.created_at = datetime.now()
        self.status = "pending"

    @abstractmethod
    def execute(self):
        pass

    def log_start(self):
        log.info(f"Task [{self.name}] starting...")
        self.status = "running"

    def log_complete(self):
        log.info(f"Task [{self.name}] completed successfully")
        self.status = "completed"

    def log_error(self, error):
        log.error(f"Task [{self.name}] failed: {error}")
        self.status = "failed"


# Concrete Task Implementations
class BackupTask(Task):
    """
    Backup task - simulates database/file backup operation.
    """

    def execute(self):
        """Run backup procedure."""
        self.log_start()
        try:
            # Simulate backup operation
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = DATA_DIR / f"backup_{timestamp}.json"

            # Create backup data
            backup_data = {"timestamp": timestamp, "type": "full_backup", "status": "completed"}

            # Save backup data
            save_json(backup_file, backup_data)

            self.log_complete()
            return {"status": "success", "file": str(backup_file), "timestamp": timestamp}
        except Exception as e:
            self.log_error(str(e))
            return {"status": "failed", "error": str(e)}


class CleanupTask(Task):
    """
    Cleanup task - removes old temporary files.
    """

    def execute(self):
        """Run cleanup procedure"""
        self.log_start()
        try:
            # Simulate cleanup operation
            cleaned_files = []

            log.info("Scanning for temporary files...")
            log.info("Removing old cache entries...")
            log.info("Cleanup completed")

            self.log_complete()
            return {
                "status": "success",
                "files_removed": len(cleaned_files),
                "space_freed": "0 MB",  # Simulated
            }
        except Exception as e:
            self.log_error(str(e))
            return {"status": "failed", "error": str(e)}


class ReportTask(Task):
    """
    Report generation task - created system status report.
    """

    def execute(self):
        """Generate and save report"""
        self.log_start()
        try:
            # Simulate report creation
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = DATA_DIR / f"report_{timestamp}.json"

            # Generate report data
            report_data = {
                "generated_at": timestamp,
                "system_status": "operational",
                "tasks_completed": 0,  # Would pull from database
                "tasks_pending": 0,
                "last_backup": "N/A",
            }

            save_json(report_file, report_data)

            self.log_complete()
            return {"status": "success", "report_file": str(report_file)}
        except Exception as e:
            self.log_error(str(e))
            return {"status": "failed", "error": str(e)}


# Factory Pattern - Task Creation
class TaskFactory:
    """
    Factory for creating Task objects.
    Centralizes task creation logic.
    """

    # Registry of available task types
    _task_registry = {
        "backup": BackupTask,
        "cleanup": CleanupTask,
        "report": ReportTask,
    }

    @classmethod
    def create(cls, task_type, name=None):
        task_class = cls._task_registry.get(task_type.lower())

        if task_class is None:
            available = ", ".join(cls._task_registry.keys())
            raise ValueError(f"Unknown task type: '{task_type}'. " f"Available types: {available}")
        return task_class(name=name)

    @classmethod
    def register(cls, task_type, task_class):
        if not issubclass(task_class, Task):
            raise TypeError(f"{task_class} must inherit from Task")

        cls._task_registry[task_type.lower()] = task_class
        log.info(f"Registered new task type: {task_type}")

    @classmethod
    def list_types(cls):
        return list(cls._task_registry.keys())


# Convenience Functions
def run_task(task_type, name=None):
    task = TaskFactory.create(task_type, name=name)
    return task.execute()


# Modular Exports
__all__ = [
    "Task",
    "BackupTask",
    "CleanupTask",
    "ReportTask",
    "TaskFactory",
    "run_task",
]
