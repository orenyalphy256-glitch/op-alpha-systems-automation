"""
Unit tests for core utility functions.

Test cover:
- JSON file operations
- Logging functionality
- Configuration management
"""
import pytest
import os
import json
import logging
from autom8 import core

# JSON operations tests
class TestJSONOperations:
    """Test JSON file operations."""
    
    def test_save_json(self, temp_file):
        """Test saving data to JSON file."""
        # Arrange
        data = {"name": "Test", "value": 123}
        
        # Act
        core.save_json(temp_file, data)
        
        # Assert
        assert os.path.exists(temp_file)
        with open(temp_file, 'r') as f:
            loaded = json.load(f)
        assert loaded == data
    
    def test_load_json_existing_file(self, temp_file):
        """Test loading data from existing JSON file."""
        # Arrange
        data = {"key": "value", "number": 42}
        with open(temp_file, 'w') as f:
            json.dump(data, f)
        
        # Act
        loaded = core.load_json(temp_file)
        
        # Assert
        assert loaded == data
    
    def test_load_json_nonexistent_file(self):
        """Test loading from non-existent file returns empty dict."""
        # Arrange
        nonexistent = "nonexistent_file_12345.json"
        
        # Act
        result = core.load_json(nonexistent)
        
        # Assert
        assert result == {}
    
    def test_save_json_complex_data(self, temp_file):
        """Test saving complex nested data structures."""
        # Arrange
        complex_data = {
            "users": [
                {"id": 1, "name": "Alice", "active": True},
                {"id": 2, "name": "Bob", "active": False}
            ],
            "metadata": {
                "version": "1.0",
                "timestamp": "2025-01-01T12:00:00"
            }
        }
        
        # Act
        core.save_json(temp_file, complex_data)
        loaded = core.load_json(temp_file)
        
        # Assert
        assert loaded == complex_data
        assert len(loaded["users"]) == 2
        assert loaded["users"][0]["name"] == "Alice"
    
    def test_save_json_overwrites_existing(self, temp_file):
        """Test that saving overwrites existing file."""
        # Arrange
        original = {"old": "data"}
        new = {"new": "data"}
        
        core.save_json(temp_file, original)
        
        # Act
        core.save_json(temp_file, new)
        loaded = core.load_json(temp_file)
        
        # Assert
        assert loaded == new
        assert "old" not in loaded
    
# Logging tests
class TestLogging:
    """Test logging functionality."""
    
    def test_logger_exists(self):
        """Test that logger is properly initialized."""
        # Act
        logger = core.log
        
        # Assert
        assert logger is not None
        assert isinstance(logger, logging.Logger)
    
    def test_log_info_message(self, caplog):
        """Test logging info message."""
        # Arrange
        message = "Test info message"
        
        # Act
        core.log.info(message)
        
        # Assert
        assert message in caplog.text
        assert "INFO" in caplog.text
    
    def test_log_error_message(self, caplog):
        """Test logging error message."""
        # Arrange
        message = "Test error message"
        
        # Act
        core.log.error(message)
        
        # Assert
        assert message in caplog.text
        assert "ERROR" in caplog.text
    
    def test_log_warning_message(self, caplog):
        """Test logging warning message."""
        # Arrange
        message = "Test warning message"
        
        # Act
        core.log.warning(message)
        
        # Assert
        assert message in caplog.text
        assert "WARNING" in caplog.text

# Path Operations Tests
class TestPathOperations:
    """Test path and directory operations."""
    
    def test_data_dir_exists(self):
        """Test that DATA_DIR is properly configured."""
        # Act
        data_dir = core.DATA_DIR
        
        # Assert
        assert data_dir is not None
        # DATA_DIR is a Path object, not a string
        from pathlib import Path
        assert isinstance(data_dir, Path)
        assert data_dir.exists()

    
    def test_base_dir_exists(self):
        """Test that BASE_DIR is properly configured."""
        # Act
        base_dir = core.BASE_DIR
        
        # Assert
        assert base_dir is not None
        # BASE_DIR is also a Path object
        from pathlib import Path
        assert isinstance(base_dir, Path)
        assert base_dir.exists()


# Utility function tests
@pytest.mark.parametrize("input_data,expected", [
    ({"a": 1, "b": 2}, {"a": 1, "b": 2}),
    ({}, {}),
    ({"nested": {"key": "value"}}, {"nested": {"key": "value"}}),
])
def test_json_roundtrip(temp_file, input_data, expected):
    """
    Test that data survives save/load cycle (roundtrip).
    Parametrized to test multiple data structures.
    """
    # Act
    core.save_json(temp_file, input_data)
    result = core.load_json(temp_file)
    
    # Assert
    assert result == expected