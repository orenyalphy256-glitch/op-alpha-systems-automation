"""
Unit tests for task functions.

Tests cover:
- Individual task execution
- Task error handling
- Task return values
"""
import pytest
from unittest.mock import Mock, patch
from autom8 import tasks

# Sample task tests
class TestSampleTasks:
    """Test sample tasks from tasks.py."""
    
    def test_backup_task_success(self, caplog):
        """Test backup task executes successfully."""
        # Act
        task = tasks.BackupTask()
        result = task.execute()
        
        # Assert
        assert result is not None
        assert result["status"] == "success"
    
    def test_cleanup_task_success(self, caplog):
        """Test cleanup task executes successfully."""
        # Act
        task = tasks.CleanupTask()
        result = task.execute()
        
        # Assert
        assert result is not None
        assert result["status"] == "success"
    
    def test_report_task_success(self, caplog):
        """Test report task executes successfully."""
        # Act
        task = tasks.ReportTask()
        result = task.execute()
        
        # Assert
        assert result is not None
        assert result["status"] == "success"

# Task error handling tests
class TestTaskErrorHandling:
    """Test task error handling."""
    
    @patch('autom8.tasks.save_json')
    def test_task_handles_external_failure(self, mock_save_json):
        """Test task handles external service failures gracefully."""
        # Arrange - Make save_json raise an exception
        mock_save_json.side_effect = Exception("Disk full")
        
        # Act - Execute BackupTask which uses save_json
        task = tasks.BackupTask()
        result = task.execute()
        
        # Assert - Task should handle exception and return failure status
        assert result is not None
        assert result["status"] == "failed"
        assert "error" in result

# Task timing tests
class TestTaskTiming:
    """Test task execution timing."""
    
    def test_backup_task_completes_fast(self):
        """Test that backup task completes within reasonable time."""
        import time
        
        # Act
        start = time.time()
        task = tasks.BackupTask()
        task.execute()
        duration = time.time() - start
        
        # Assert
        assert duration < 5.0, "Backup task should complete in under 5 seconds"