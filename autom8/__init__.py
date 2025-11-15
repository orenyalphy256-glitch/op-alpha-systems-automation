# Core utilities - expose at package level
from autom8.core import (
    log,
    load_json,
    save_json,
    setup_logging,
    DATA_DIR,
    LOGS_DIR,
    BASE_DIR,
    PROJECT_ROOT,
)

# Package metadata
__version__ = "0.1.0"
__author__ = "Alphonce Liguori"
__email__ = "orenyalphy256@gmail.com"

# Define public API (what users can import)
__all__ = [
    "logs",
    "load_json",
    "save_json",
    "setup_logging",
    "DATA_DIR",
    "LOGS_DIR",
    "BASE_DIR",
    "PROJECT_ROOT",
]