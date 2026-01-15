# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""

tasks.py - Task Management with Design Patterns
Implements: Factory Pattern, Abstract Base Class (ABC)
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

from autom8.core import DATA_DIR, log, save_json


class TaskConfig:
    """Container for task configuration to decouple from hardcoded paths/patterns."""

    def __init__(self, base_path=None, filename_pattern=None):
        self.base_path = Path(base_path) if base_path else DATA_DIR
        self.filename_pattern = filename_pattern


# Abstract Base Class - Task Interface
class Task(ABC):
    """
    Abstract base class defining the Task interface
    All task types must inherit from this and implement execute().
    """

    def __init__(self, name=None, config=None):
        """
        Initialize task with optional name and config injection.
        Args:
            name (str): Human-readable task name
            config (TaskConfig): Configuration object
        """
        self.name = name or self.__class__.__name__
        self.config = config or TaskConfig()
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
            # Simulate backup operation using injected config
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pattern = self.config.filename_pattern or "backup_{}.json"
            backup_file = self.config.base_path / pattern.format(timestamp)

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
            # Simulate report creation using injected config
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pattern = self.config.filename_pattern or "report_{}.json"
            report_file = self.config.base_path / pattern.format(timestamp)

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

        # In a real system, we'd load these from Config per task type
        from autom8.config import Config

        config = TaskConfig(base_path=Config.DATA_DIR)

        return task_class(name=name, config=config)

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
