
import pytest
from unittest.mock import patch, MagicMock
from autom8.tasks import (
    Task, TaskFactory, BackupTask, CleanupTask, ReportTask, run_task
)

class ConcreteTask(Task):
    def execute(self):
        return "Executed"

def test_task_abstract_instantiation():
    # Cannot instantiate abstract class
    with pytest.raises(TypeError):
        Task()

def test_concrete_task():
    t = ConcreteTask(name="Test")
    assert t.name == "Test"
    assert t.status == "pending"
    assert t.execute() == "Executed"

def test_task_logging():
    t = ConcreteTask()
    with patch("autom8.tasks.log") as mock_log:
        t.log_start()
        assert t.status == "running"
        mock_log.info.assert_called()
        
        t.log_complete()
        assert t.status == "completed"
        
        t.log_error("Err")
        assert t.status == "failed"
        mock_log.error.assert_called()

def test_task_factory_create():
    t = TaskFactory.create("backup")
    assert isinstance(t, BackupTask)
    
    t = TaskFactory.create("cleanup")
    assert isinstance(t, CleanupTask)
    
    with pytest.raises(ValueError):
        TaskFactory.create("unknown")

def test_task_factory_register():
    class NewTask(Task):
        def execute(self): pass
        
    TaskFactory.register("new", NewTask)
    t = TaskFactory.create("new")
    assert isinstance(t, NewTask)
    
    # Invalid registration
    class BadTask: pass
    with pytest.raises(TypeError):
        TaskFactory.register("bad", BadTask)
        
    assert "new" in TaskFactory.list_types()

@patch("autom8.tasks.save_json")
def test_backup_task(mock_save):
    t = BackupTask()
    res = t.execute()
    assert res["status"] == "success"
    mock_save.assert_called()
    
    # Failure
    mock_save.side_effect = Exception("Fail")
    res = t.execute()
    assert res["status"] == "failed"

def test_cleanup_task():
    t = CleanupTask()
    res = t.execute()
    assert res["status"] == "success"

@patch("autom8.tasks.save_json")
def test_report_task(mock_save):
    t = ReportTask()
    res = t.execute()
    assert res["status"] == "success"

def test_run_task_helper():
    with patch("autom8.tasks.TaskFactory.create") as mock_create:
        mock_task = MagicMock()
        mock_create.return_value = mock_task
        run_task("backup", "MyBackup")
        mock_task.execute.assert_called()