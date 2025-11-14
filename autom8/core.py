"""
core.py - Shared Utilities & Configurations for Autom8 Package
Purpose: Centralize common functions and configurations used across the application.
"""
import os
import json
import logging
from pathlib import Path

# Get absolute path to autom8 package directory
BASE_DIR = Path(__file__).parent.absolute()

# Project root (one level up from autom8/)
PROJECT_ROOT = BASE_DIR.parent

# Data directory (outside package, for databases/files)
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# Logs directory (outside package, for databases/files)
LOGS_DIR = PROJECT_ROOT.parent / "99-Logs"
LOGS_DIR.mkdir(exist_ok=True)