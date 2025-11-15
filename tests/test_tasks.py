"""
test_tasks.py - Unit tests for task system
Run with: pytest tests/test_tasks.py -v
"""
import pytest
from autom8.tasks import TaskFactory, Task, BackupTask

def test_factory_creates_backup_task():
    """Factory should create BackupTask instance."""
    task = TaskFactory.create("backup")
    assert isinstance(task, BackupTask)
    assert isinstance(task, Task)

def test_factory_raises_on_invalid_type():
    """Factory should raise ValueError for unknown task type."""
    with pytest.raises(ValueError, match="Unknown task type"):
        TaskFactory.create("nonexistent")

def test_backup_task_executes():
    """Backup task should execute and return success."""
    task = TaskFactory.create("backup")
    result = task.execute()
    assert result["status"] == "success"
    assert "file" in result
    assert "timestamp" in result

def test_cleanup_task_executes():
    """Cleanup task should execute successfully."""
    task = TaskFactory.create("cleanup")
    result = task.execute()
    assert result["status"] == "success"

def test_factory_list_types():
    """Factory should list all available task types."""
    types = TaskFactory.list_types()
    assert "backup" in types
    assert "cleanup" in types
    assert "report" in types

def test_task_has_name_and_status():
    """Task should track name and status."""
    task = TaskFactory.create("backup", name="NightlyBackup")
    assert task.name == "NightlyBackup"
    assert task.status == "pending"