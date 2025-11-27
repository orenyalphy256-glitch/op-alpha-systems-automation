"""
core.py - Shared Utilities & Configuration
Purpose: Centralize common functions used across the application
"""
import os
import json
import logging
from pathlib import Path

# Directory Configuration

# Get absolute path to autom8 package directory
BASE_DIR = Path(__file__).parent.absolute()

# Project root directory
PROJECT_ROOT = BASE_DIR.parent

# Data directory
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# Logs directory
LOGS_DIR = PROJECT_ROOT.parent / "99-Logs"
LOGS_DIR.mkdir(exist_ok=True)

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
    
# Logging Configuration
def setup_logging(log_file="system.log", level=logging.INFO):
    log_path = LOGS_DIR / log_file

    # Create formatter with timestamp, level, and message
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File Handler (writes to file)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)

    # Console Handler (prints to terminal)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger

# Initialize logging on module import
log = setup_logging()

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
]
