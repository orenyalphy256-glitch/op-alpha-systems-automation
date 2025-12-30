# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.

from datetime import datetime
from autom8.models import Contact, TaskLog


def test_contact_model_methods():
    c = Contact(name="Test", phone="123", email="test@test.com")
    c.id = 1
    c.created_at = datetime(2025, 1, 1, 10, 0, 0)
    c.updated_at = datetime(2025, 1, 1, 10, 0, 0)

    d = c.to_dict()
    assert d["id"] == 1
    assert d["name"] == "Test"
    assert d["phone"] == "123"
    assert d["email"] == "test@test.com"
    # notes removed
    assert "created_at" in d
    assert "updated_at" in d

    # Test __repr__ if it exists (usually sqla adds one or we define one)
    assert "Contact" in repr(c)
    assert "Test" in repr(c)


def test_tasklog_model_methods():
    t = TaskLog(
        task_type="backup", status="completed", result_data="ok", error_message=None
    )
    t.id = 1
    t.started_at = datetime(2025, 1, 1, 10, 0, 0)
    t.completed_at = datetime(2025, 1, 1, 10, 5, 0)

    d = t.to_dict()
    assert d["id"] == 1
    assert d["task_type"] == "backup"
    assert d["status"] == "completed"
    assert d["result_data"] == "ok"
    # duration_seconds is not in to_dict

    assert "TaskLog" in repr(t)
    assert "backup" in repr(t)

