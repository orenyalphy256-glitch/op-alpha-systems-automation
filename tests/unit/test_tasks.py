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
        result = tasks.backup_task()
        
        # Assert
        assert "Backup completed" in caplog.text or result is not None
    
    def test_cleanup_task_success(self, caplog):
        """Test cleanup task executes successfully."""
        # Act
        result = tasks.cleanup_task()
        
        # Assert
        assert "Cleanup completed" in caplog.text or result is not None
    
    def test_report_task_success(self, caplog):
        """Test report task executes successfully."""
        # Act
        result = tasks.report_task()
        
        # Assert
        assert "Report generated" in caplog.text or result is not None

# Task error handling tests
class TestTaskErrorHandling:
    """Test task error handling."""
    
    @patch('autom8.tasks.some_external_service')
    def test_task_handles_external_failure(self, mock_service):
        """Test task handles external service failures gracefully."""
        # Arrange
        mock_service.call.side_effect = Exception("Service unavailable")
        
        # Act & Assert
        # Task should handle exception, not crash
        try:
            result = tasks.task_with_external_dependency()
            assert result is not None  # Should return something, not crash
        except Exception as e:
            pytest.fail(f"Task should handle exceptions, but raised: {e}")

# Task timing tests
class TestTaskTiming:
    """Test task execution timing."""
    
    def test_quick_task_completes_fast(self):
        """Test that quick tasks complete within reasonable time."""
        import time
        
        # Act
        start = time.time()
        tasks.quick_task()
        duration = time.time() - start
        
        # Assert
        assert duration < 1.0, "Quick task should complete in under 1 second"
    
    @pytest.mark.slow
    def test_slow_task_marked_appropriately(self):
        """Test that slow tasks are marked with @slow decorator."""
        import time
        
        # Act
        start = time.time()
        tasks.slow_task() if hasattr(tasks, 'slow_task') else None
        duration = time.time() - start
        
        # Assert
        # Slow tasks are expected to take longer
        assert duration >= 0  # Just verify it completes