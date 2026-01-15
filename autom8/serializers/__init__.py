# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""
serializers/ - API Contract Definitions

STABLE API CONTRACT
-------------------
WARNING: This module defines the Public API Contract (Zone 2).
CHANGES HERE BREAK CLIENTS (Integrators, Mobile, Web).

1. FROZEN FIELDS: Existing fields must NEVER be removed or renamed.
2. TYPES: Field data types (str, int, bool) must NEVER change.
3. ADDITIVE ONLY: You may only ADD new fields (which must be nullable/optional).
4. NO POLYMORPHISM: Response shapes must be static. No `if type == x return dict A else dict B`.

VIOLATION OF THESE RULES WILL CAUSE CRITICAL SYSTEM FAILURE.
"""

from .contacts import serialize_contact, serialize_contacts_page
from .info import serialize_health_check, serialize_system_info
from .tasklogs import serialize_task_log, serialize_task_logs_list, serialize_task_stats

__all__ = [
    "serialize_contact",
    "serialize_contacts_page",
    "serialize_task_log",
    "serialize_task_logs_list",
    "serialize_task_stats",
    "serialize_system_info",
    "serialize_health_check",
]
