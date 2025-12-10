"""
Quick test module for autom8.paths
"""

from autom8.core import BASE_DIR, PROJECT_ROOT, DATA_DIR, LOGS_DIR

print("Path Verification:")
print("=" * 60)
print(f"BASE_DIR (autom8/): {BASE_DIR}")
print(f"PROJECT_ROOT: {PROJECT_ROOT}")
print(f"DATA_DIR: {DATA_DIR}")
print(f"LOGS_DIR: {LOGS_DIR}")
print("=" * 60)

# Check if directories exist
print("\nDirectory Status:")
print(f"DATA_DIR exists: {DATA_DIR.exists()}")
print(f"LOGS_DIR exists: {LOGS_DIR.exists()}")
