"""
monitor_scheduler.py - Monitor scheduler status
Display scheduler status and recent job executions

Run: python -m autom8.monitor_scheduler
"""
import time
import os
from datetime import datetime, timedelta
from autom8.scheduler import get_scheduled_jobs
from autom8.models import get_session, TaskLog

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def format_timedelta(td):
    """Format timedelta for display."""
    if td is None:
        return "N/A"
    
    total_seconds = int(td.total_seconds())
    if total_seconds < 60:
        return f"{total_seconds}s"
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}m {seconds}s"
    else:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    
def monitor_dashboard():
    """Display real-time scheduler status and recent job executions."""
    try:
        while True:
            clear_screen()
            print("=" * 70)
            print("" * 20 + "AUTOM8 SCHEDULER MONITOR")
            print("=" * 70)
            print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
            # Scheduled Jobs
            print("SCHEDULED JOBS")
            print("-" * 70)
            jobs = get_scheduled_jobs()

            if not jobs:
                print("No scheduled jobs found.")
            else:
                for job in jobs:
                    next_run = job.get('next_run_time')
                    if next_run:
                        next_run_dt = datetime.fromisoformat(next_run)
                        time_until = next_run_dt - datetime.now()
                        time_str = format_timedelta(time_until)
                    else:
                        time_str = "N/A"

                    print(f"  - {job['name']}")
                    print(f"    Next Run: {next_run} (in {time_str})")
                    print()

            # Recent Task Executions
            print("\nRECENT TASK EXECUTIONS (last 10)")
            print("-" * 70)

            session = get_session()
            try:
                logs = session.query(TaskLog).order_by(
                    TaskLog.started_at.desc()
                ).limit(10).all()

                if not logs:
                    print("No task logs yet")
                else:
                    for log in logs:
                        status_emoji = {
                            'completed': '✅',
                            'failed': '❌',
                            'running': '⏳'
                        }.get(log.status, '❓')

                        duration = None
                        if log.completed_at and log.started_at:
                            duration = log.completed_at - log.started_at

                        print(f"  - {status_emoji} {log.task_type.upper()}")
                        print(f"    Started: {log.started_at}")
                        print(f"    Status: {log.status}")
                        if duration:
                            print(f"    Duration: {format_timedelta(duration)}")
                        if log.error_message:
                            print(f"    Error: {log.error_message[:60]}...")
                        print()

                    # Statistics
                    print("\nSTATISTICS")
                    print("-" * 70)
                    
                    total = session.query(TaskLog).count()
                    completed = session.query(TaskLog).filter(
                        TaskLog.status == "completed"
                    ).count()
                    failed = session.query(TaskLog).filter(
                        TaskLog.status == "failed"
                    ).count()
                    
                    success_rate = (completed / total * 100) if total > 0 else 0

                    print(f"  - Total Executions: {total}")
                    print(f"  - Completed: {completed}")
                    print(f"  - Failed: {failed}")
                    print(f"  - Success Rate: {success_rate:.1f}%")

            finally:
                session.close()

            print("\n" + "=" * 70)
            print("Press Ctrl+C to exit | Refreshes every 5 seconds.")

            time.sleep(5)

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")

if __name__ == "__main__":
    monitor_dashboard()