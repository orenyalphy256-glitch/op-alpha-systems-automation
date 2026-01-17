# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""
config.py - Application Configuration
Purpose: Define and manage application configuration settings
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    APP_NAME = os.getenv("APP_NAME", "Autom8")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    ENVIRONMENT = os.getenv("ENVIRONMENT") or os.getenv("APP_ENV") or "development"
    DEBUG = (os.getenv("DEBUG") or os.getenv("APP_DEBUG") or "False").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY")

    API_HOST = os.getenv("API_HOST", "127.0.0.1")
    API_PORT = int(os.getenv("API_PORT", 5000))
    TIMEZONE = os.getenv("TIMEZONE", "UTC")

    PROJECT_ROOT = Path(__file__).parent.parent.absolute()
    DATA_DIR = PROJECT_ROOT / "data"
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/system.db")
    DB_ECHO = os.getenv("DB_ECHO", "False").lower() == "true"

    LICENSE_MODE = os.getenv("AUTOM8_MODE", "community")

    PROTECT_SIGNATURE = os.getenv("AUTOM8_SIGNATURE", "")
    ENABLE_PRO = os.getenv("AUTOM8_PRO", "false").lower() == "true"
    AUTOM8_LICENSE_KEY = os.getenv("AUTOM8_LICENSE_KEY")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Scheduling Configuration
    BACKUP_INTERVAL_HOURS = int(os.getenv("BACKUP_INTERVAL_HOURS", 24))
    REPORT_CRON_EXPRESSION = os.getenv("REPORT_CRON_EXPRESSION", "0 9 * * *")
