"""
scheduler.py - Job Scheduling with APScheduler
Integrates: Task system + Database logging
"""
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from autom8.core import log, DATA_DIR
from autom8.tasks import TaskFactory, run_task
from autom8.models import get_session, TaskLog, init_db
from autom8.alerts import alert_task_failure

# Scheduler configuration
scheduler = None # Global scheduler instance

# Job execution with database logging
def execute_task_with_logging(task_type, task_name=None):
    session = get_session()

    # Create task log entry
    task_log = TaskLog(
        task_type=task_type,
        task_name=task_name or task_type,
        status="running",
        started_at=datetime.utcnow()
    )

    try:
        # Add log entry
        session.add(task_log)
        session.commit()
        session.refresh(task_log)

        log.info(f"Starting scheduled task: {task_type} (log ID: {task_log.id})")

        result = run_task(task_type, name=task_name)

        # Update log entry
        task_log.status = "completed"
        task_log.completed_at = datetime.utcnow()
        task_log.result_data = str(result)[:500]  # Truncate if too huge

        session.commit()

        log.info(f"Completed scheduled task: {task_type} (log ID: {task_log.id})")

        return result
    
    except Exception as e:
        task_log.status = "failed"
        task_log.completed_at = datetime.utcnow()
        task_log.error_message = str(e)[:500]

        session.commit()

        log.error(f"Failed scheduled task: {task_type} (log ID: {task_log.id}): {e}")

        # Send alert
        alert_task_failure(task_type, str(e))

        return {"status": "failed", "error": str(e)}
    
    finally:
        session.close()

# Scheduler event listeners
def job_executed_listener(event):
    log.info(f"Job {event.job_id} executed successfully")

def job_error_listener(event):
    log.error(f"Job {event.job_id} failed: {event.exception}")

# Scheduler initialization
def init_scheduler():
    global scheduler

    if scheduler is not None:
        log.warning("Scheduler already initialized")
        return scheduler
    
    # Ensure database is initialized
    init_db()

    # Create scheduler with thread pool executor
    scheduler = BackgroundScheduler(
        timezone="UTC",
        job_defaults={
            'coalesce': False, # Run all missed jobs not just latest
            'max_instances': 3, # Allow up to 3 concurrent instances of the same job
            'misfire_grace_time': 60 # Allow 60 seconds grace for missed jobs
        }
    )

    # Add event listeners
    scheduler.add_listener(job_executed_listener, EVENT_JOB_EXECUTED)
    scheduler.add_listener(job_error_listener, EVENT_JOB_ERROR)

    log.info("Scheduler initialized")

    return scheduler

# Job scheduling functions
def schedule_backup_job():
    if scheduler is None:
        raise RuntimeError("Scheduler not initialized. Call init_scheduler() first.")
    
    scheduler.add_job(
        func=execute_task_with_logging,
        trigger=IntervalTrigger(hours=24),
        args=['backup'],
        id='backup_job',
        name='Daily Backup Task',
        replace_existing=True,
        next_run_time=datetime.utcnow() # Run immediately on first start
    )

    log.info("Backup job scheduled successfully")

def schedule_cleanup_job():
    if scheduler is None:
        raise RuntimeError("Scheduler not initialized. Call init_scheduler() first.")
    
    scheduler.add_job(
        func=execute_task_with_logging,
        trigger=IntervalTrigger(hours=1),
        args=['cleanup'],
        id='cleanup_job',
        name='Hourly Cleanup Task',
        replace_existing=True
    )

    log.info("Cleanup job scheduled successfully")

def schedule_report_job():
    if scheduler is None:
        raise RuntimeError("Scheduler not initialized. Call init_scheduler() first.")
    
    scheduler.add_job(
        func=execute_task_with_logging,
        trigger=CronTrigger(hour=9, minute=0),
        args=['report'],
        id='report_job',
        name='Daily Report Task',
        replace_existing=True
    )

    log.info("Report job scheduled successfully")

def schedule_all_jobs():
    schedule_backup_job()
    schedule_cleanup_job()
    schedule_report_job()

    log.info("All default jobs scheduled successfully")

# Scheduler management
def start_scheduler():
    if scheduler is None:
        raise RuntimeError("Scheduler not initialized. Call init_scheduler() first.")
    
    if not scheduler.running:
        scheduler.start()
        log.info("Scheduler started successfully")
    else:
        log.warning("Scheduler already running")

def stop_scheduler(wait=True):
    if scheduler is None:
        log.warning("Scheduler not initialized")
        return
    
    if scheduler.running:
        scheduler.shutdown(wait=wait)
        log.info("Scheduler stopped successfully")
    else:
        log.warning("Scheduler not running")

def get_scheduled_jobs():
    if scheduler is None:
        return []
    
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run_time': (job.next_run_time.isoformat() if getattr(job, 'next_run_time', None) else 'N/A'),
            'trigger': str(job.trigger)
        })

    return jobs

def pause_job(job_id):
    if scheduler is None:
        raise RuntimeError("Scheduler not initialized")
    
    scheduler.pause_job(job_id)
    log.info(f"Job {job_id} paused successfully")

def resume_job(job_id):
    if scheduler is None:
        raise RuntimeError("Scheduler not initialized")
    
    scheduler.resume_job(job_id)
    log.info(f"Job {job_id} resumed successfully")

def remove_job(job_id):
    if scheduler is None:
        raise RuntimeError("Scheduler not initialized")
    
    scheduler.remove_job(job_id)
    log.info(f"Job {job_id} removed successfully")

def run_job_now(job_id):
    if scheduler is None:
        raise RuntimeError("Scheduler not initialized")
    
    job = scheduler.get_job(job_id)
    if job is None:
        raise ValueError(f"Job {job_id} not found")
    
    # Execute job function immediately
    job.func(*job.args, **job.kwargs)
    log.info(f"Manually executed job {job_id} successfully")

# Module exports
__all__ = [
    'scheduler',
    'init_scheduler',
    'start_scheduler',
    'stop_scheduler',
    'get_scheduler',
    'schedule_backup_job',
    'schedule_cleanup_job',
    'schedule_report_job',
    'schedule_all_jobs',
    'get_scheduled_jobs',
    'pause_job',
    'resume_job',
    'remove_job',
    'run_job_now',
    'execute_task_with_logging',
]