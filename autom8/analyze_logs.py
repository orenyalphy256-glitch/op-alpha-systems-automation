"""
analyze_logs.py - Log analysis tool
Parse and analyze JSON logs
Usage: python -m autom8.analyze_logs # Run for last 24 hours
python -m autom8.analyze_logs --hours 48 # Run for last 48 hours
"""
import json
from pathlib import Path
from collections import Counter
from datetime import datetime, timedelta
from autom8.core import log, LOGS_DIR

def parse_json_logs(log_file="autom8_json.log", hours=24):
    log_path = LOGS_DIR / log_file

    if not log_path.exists():
        print(f"JSON log file not found: {log_path}")
        return []
    
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    entries = []

    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                timestamp = datetime.fromisoformat(entry["timestamp"].replace("Z", ""))

                if timestamp >= cutoff_time:
                    entries.append(entry)
            except json.JSONDecodeError:
                continue

    return entries

def analyze_log_levels(entries):
    levels = Counter(entry["level"] for entry in entries)

    print("\n Log Levels Distribution")
    print("-" * 50)
    for level, count in levels.most_common():
        print(f"  {level:10} : {count:5} entries")

    return levels

def analyze_errors(entries):
    errors = [e for e in entries if e['level'] in ['ERROR', 'CRITICAL']]

    print(f"\n ERRORS ({len(errors)} total)")
    print("-" * 50)
    
    if not errors:
        print("  No errors found")
        return
    
    for error in errors[-10:]: # Last 10 errors
        print(f"\n [{error['timestamp']}] {error['level']}")
        print(f"  Message: {error['message']}")
        print(f"  Module: {error['module']} -> {error['function']}() line {error['line']}")
        if 'exception' in error:
            print(f"  Exception: {error['exception'][:100]}...")

def analyze_modules(entries):
    modules = Counter(entry["module"] for entry in entries)

    print("\n Most Active Modules")
    print("-" * 50)
    for module, count in modules.most_common(10):
        print(f"  {module:20} : {count:5} entries")

def generate_report(hours=24):
    print("=" * 70)
    print(" " * 20)
    print("=" * 70)
    print(f"Time windows: Last {hours} hours")
    print(f"Analysis time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    entries = parse_json_logs(hours=hours)

    if not entries:
        print("\nNo log entries found in specified time window.")
        return
    
    print(f"\nTotal entries: {len(entries)}")

    analyze_log_levels(entries)
    analyze_modules(entries)
    analyze_errors(entries)

    print("\n" + "=" * 70)
    print(" Analysis complete")
    print("=" * 70)

if __name__ == "__main__":
    import sys
    hours = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    generate_report(hours)