"""
logging_config.py - Advanced Logging Configuration
Implements: JSON structured logging, rotation, multiple handlers
"""
import os
import json
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
from pathlib import Path

from autom8.core import LOGS_DIR

# JSON Formatter
class JSONFormatter(logging.Formatter):
    """Format log records as JSON(JSONL - one JSON object per line)"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.funcName,
            "line": record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields (custom context)
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)

        return json.dumps(log_data)
    
# Logging Setup
def setup_advanced_logging(
    app_name="autom8",
    log_level=logging.INFO,
    console_output=True,
    json_logs=True,
    text_logs=True,
    rotation_size_mb=10,
    backup_count=5
):
    """Configure comprehensive logging system."""

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers (avoid duplicates)
    root_logger.handlers.clear()

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # JSON File handler
    if json_logs:
        json_log_path = LOGS_DIR / f"{app_name}_json.log"
        json_handler = RotatingFileHandler(
            json_log_path,
            maxBytes=rotation_size_mb * 1024 * 1024,
            backupCount=backup_count,
            encoding='utf-8'
        )
        json_handler.setLevel(log_level)
        json_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(json_handler)

    # Text File handler
    if text_logs:
        text_log_path = LOGS_DIR / f"{app_name}_text.log"
        text_handler = RotatingFileHandler(
            text_log_path,
            maxBytes=rotation_size_mb * 1024 * 1024,
            backupCount=backup_count,
            encoding='utf-8'
        )
        text_handler.setLevel(log_level)
        text_formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d:%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        text_handler.setFormatter(text_formatter)
        root_logger.addHandler(text_handler)

    # Error File handler
    error_log_path = LOGS_DIR / f"{app_name}_errors.log"
    error_handler = RotatingFileHandler(
        error_log_path,
        maxBytes=rotation_size_mb * 1024 * 1024,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR) # Only ERROR AND CRITICAL
    error_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s\nLocation: %(pathname)s:%(lineno)d\n%(message)s\n",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    error_handler.setFormatter(error_formatter)
    root_logger.addHandler(error_handler)

    root_logger.info(f"Advanced logging configured for {app_name}")
    root_logger.info(f"Log files: {LOGS_DIR}")

    return root_logger

# Context Logger
class ContextLogger:
    """
    Helper for adding context to log messages.
    Enables structured logging with extra fields.
    """

    def __init__(self, logger_name=None):
        self.logger = logging.getLogger(logger_name or __name__)

    def log_with_context(self, level, message, **context):
        extra_data = context
        self.logger.log(
            getattr(logging, level.upper()),
            message,
            extra={'extra_data': extra_data}
        )

    def info(self, message, **context):
        """Log INFO with context."""
        self.log_with_context("INFO", message, **context)

    def warning(self, message, **context):
        """Log WARNING with context."""
        self.log_with_context("WARNING", message, **context)

    def error(self, message, **context):
        """Log ERROR with context."""
        self.log_with_context("ERROR", message, **context)

    def critical(self, message, **context):
        """Log CRITICAL with context."""
        self.log_with_context("CRITICAL", message, **context)

# Module exports
__all__ = [
    'setup_advanced_logging',
    'JSONFormatter',
    'ContextLogger'
]