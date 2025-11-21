"""
metrics.py - System Metrics Collection
Collects: CPU, disk usage, task statistics
"""
import psutil
import time
from datetime import datetime
from autom8.models import get_session, TaskLog, Contact
from autom8.core import log

# System metrics
def get_system_metrics():
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "cpu": {
                "percent": cpu_percent,
                "count": psutil.cpu_count()
            },
            "memory": {
                "total": memory.total // (1024 * 1024),
                "available_mb": memory.available // (1024 * 1024),
                "used_mb": memory.used // (1024 * 1024),
                "percent": memory.percent   
            },
            "disk": {
                "total_gb": disk.total // (1024 ** 3),
                "used_gb": disk.used // (1024 ** 3),
                "free_gb": disk.free // (1024 ** 3),
                "percent": disk.percent
            }
        }
    except Exception as e:
        log.error(f"Error collecting system metrics: {e}")
        return None

# Application metrics
def get_task_metrics():
    session = get_session()
    try:
        total = session.query(TaskLog).count()
        completed = session.query(TaskLog).filter(TaskLog.status == "completed").count()
        failed = session.query(TaskLog).filter(TaskLog.status == "failed").count()
        running = session.query(TaskLog).filter(TaskLog.status == "running").count()

        success_rate = (completed / total * 100) if total > 0 else 0

        # Get last 10 executions
        recent = session.query(TaskLog).order_by(
            TaskLog.started_at.desc()
        ).limit(10).all()

        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_executions": total,
            "completed": completed,
            "failed": failed,
            "running": running,
            "success_rate": round(success_rate, 2),
            "recent_count": len(recent)
        }
    except Exception as e:
        log.error(f"Error collecting task metrics: {e}")
        return None
    finally:
        session.close()

# Database metrics
def get_database_metrics():
    """Collect database statistics."""
    session = get_session()
    try:
        contact_count = session.query(Contact).count()
        tasklog_count = session.query(TaskLog).count()

        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "contacts": contact_count,
            "task_logs": tasklog_count
        }
    except Exception as e:
        log.error(f"Error collecting database metrics: {e}")
        return None
    finally:
        session.close()

# All metrics
def get_all_metrics():
        return {
            "system": get_system_metrics(),
            "task": get_task_metrics(),
            "database": get_database_metrics()
        }
    
# Module exports
__all__ = [
    'get_system_metrics',
    'get_task_metrics',
    'get_database_metrics',
    'get_all_metrics'
]