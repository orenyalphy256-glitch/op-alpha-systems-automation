# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""

core.py - Shared Utilities & Configuration
Purpose: Centralize common functions used across the application
"""

import json
import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get absolute path to autom8 package directory
BASE_DIR = Path(__file__).parent.absolute()

# Project root directory
PROJECT_ROOT = BASE_DIR.parent

# Data directory
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# Logs directory
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)


# Configuration from the environment
class Config:
    """Application configuration from environment variables."""

    APP_NAME = os.getenv("APP_NAME", "Autom8")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    ENVIRONMENT = os.getenv("ENVIRONMENT") or os.getenv("APP_ENV") or "development"
    DEBUG = (os.getenv("DEBUG") or os.getenv("APP_DEBUG") or "False") == "True"
    SECRET_KEY = os.getenv("SECRET_KEY")
    API_HOST = os.getenv("API_HOST")
    API_PORT = int(os.getenv("API_PORT", 5000))
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/system.db")
    DB_ECHO = os.getenv("DB_ECHO", "False") == "True"
    LOG_LEVEL = os.getenv("LOG_LEVEL")
    AUTOM8_LICENSE_KEY = os.getenv("AUTOM8_LICENSE_KEY")

    # Handle potentially nested log paths from .env
    _log_file_env = os.getenv("LOG_FILE", "app.log")
    if "logs/" in _log_file_env or "logs\\" in _log_file_env:
        LOG_FILE = PROJECT_ROOT / _log_file_env
    else:
        LOG_FILE = LOGS_DIR / _log_file_env
    TIMEZONE = os.getenv("TIMEZONE")
    PROTECT_SIGNATURE = "ALO-v1-PROPRIETARY-98B2-C7"


# JSON File Operations
def load_json(filepath):
    filepath = Path(filepath)
    if not filepath.exists():
        return {}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in {filepath}: {e}")
        return {}
    except Exception as e:
        logging.error(f"Error reading {filepath}: {e}")
        return {}


def save_json(filepath, data, indent=2):
    filepath = Path(filepath)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        logging.error(f"Error writing {filepath}: {e}")
        return False


# JSON Formatter
class JSONFormatter(logging.Formatter):
    """Format log records as JSON(JSONL - one JSON object per line)"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.now().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.funcName,
            "line": record.lineno,
            "_pid": Config.PROTECT_SIGNATURE,  # Stealth signature for proprietary tracking
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields (custom context)
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        return json.dumps(log_data)


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
        self.logger.log(getattr(logging, level.upper()), message, extra={"extra_data": extra_data})

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


# Logging Configuration
def setup_logging(
    app_name="autom8",
    log_level=getattr(logging, Config.LOG_LEVEL),
    console_output=True,
    json_logs=True,
    text_logs=True,
    rotation_size_mb=10,
    backup_count=5,
):
    """Configure comprehensive logging system."""

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers (avoid duplicates)
    root_logger.handlers.clear()

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
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
            encoding="utf-8",
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
            encoding="utf-8",
        )
        text_handler.setLevel(log_level)
        text_formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d:%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        text_handler.setFormatter(text_formatter)
        root_logger.addHandler(text_handler)

    # Error File handler
    error_log_path = LOGS_DIR / f"{app_name}_errors.log"
    error_handler = RotatingFileHandler(
        error_log_path,
        maxBytes=rotation_size_mb * 1024 * 1024,
        backupCount=backup_count,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)  # Only ERROR AND CRITICAL
    error_formatter = logging.Formatter(
        fmt=(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s\n"
            "Location: %(pathname)s:%(lineno)d\n%(message)s\n"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    error_handler.setFormatter(error_formatter)
    root_logger.addHandler(error_handler)

    root_logger.info(f"Advanced logging configured for {app_name}")
    root_logger.info(f"Log files: {LOGS_DIR}")
    root_logger.info(f"Integrity check: {Config.PROTECT_SIGNATURE}")

    return root_logger


# Initialize logging on module import
log = logging.getLogger(__name__)
log.info(f"Loaded environment: {Config.ENVIRONMENT}")
log.info(f"Debug mode: {Config.DEBUG}")


# No complex provider registry in single-repo mode
def is_licensed() -> bool:
    """Check if the system has a valid license key."""
    key = Config.LICENSE_KEY
    if not key or key == "DEMO-COMMUNITY-MODE":
        return False
    return key.startswith("PRO")


# Module-Level Exports
__all__ = [
    "BASE_DIR",
    "PROJECT_ROOT",
    "DATA_DIR",
    "LOGS_DIR",
    "load_json",
    "save_json",
    "log",
    "setup_logging",
    "JSONFormatter",
    "ContextLogger",
    "Config",
    "is_licensed",
]

# AUTOM8_PROTECT_ डीएनए_MARKER = "41-4c-4f-5f-50-52-4f-50-52-49-45-54-41-52-59"
