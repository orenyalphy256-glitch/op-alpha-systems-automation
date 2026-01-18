# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""
TaskLog Resource Serializers
"""


def serialize_task_log(log_entry):
    """Serialize a TaskLog model instance."""
    if not log_entry:
        return None

    return {
        "id": log_entry.id,
        "task_type": log_entry.task_type,
        "task_name": log_entry.task_name,
        "status": log_entry.status,
        "started_at": log_entry.started_at.isoformat() if log_entry.started_at else None,
        "completed_at": log_entry.completed_at.isoformat() if log_entry.completed_at else None,
        "result": log_entry.result_data,
        "error": log_entry.error_message,
    }


def serialize_task_logs_list(logs, count=None):
    """Serialize a list of task logs."""
    return {
        "count": count if count is not None else len(logs),
        "logs": [serialize_task_log(log) for log in logs],
    }


def serialize_task_stats(total, completed, failed, running, success_rate):
    """
    Serialize task execution statistics.

    Returns:
        dict: Stats object
    """
    return {
        "total_executions": total,
        "completed": completed,
        "failed": failed,
        "running": running,
        "success_rate": round(success_rate, 2),
    }


__all__ = ["serialize_task_log", "serialize_task_logs_list", "serialize_task_stats"]
