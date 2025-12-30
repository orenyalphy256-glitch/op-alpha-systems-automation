# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.

"""
interfaces.py - Abstract interfaces for Core Proprietary Modules.
Enables "Limited Mode" in the public repository while allowing
seamless integration with Private Core modules.
"""

from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


@runtime_checkable
class SecurityProvider(Protocol):
    """Interface for Security operations."""

    def hash_password(self, password: str) -> str: ...

    def verify_password(self, password: str, password_hash: str) -> bool: ...

    def generate_token(
        self, user_id: str, additional_claims: Optional[Dict[str, Any]] = None
    ) -> str: ...

    def verify_token(self, token: str) -> Dict[str, Any]: ...

    def encrypt(self, data: str) -> str: ...

    def decrypt(self, encrypted_data: str) -> str: ...

    def sanitize_input(self, user_input: str) -> str: ...


@runtime_checkable
class SchedulerProvider(Protocol):
    """Interface for Scheduler operations."""

    def init_scheduler(self) -> Any: ...

    def start_scheduler(self) -> None: ...

    def stop_scheduler(self, wait: bool = True) -> None: ...

    def get_jobs(self) -> List[Dict[str, Any]]: ...

    def schedule_task(self, task_type: str, **kwargs) -> str: ...

    def pause_job(self, job_id: str) -> None: ...

    def resume_job(self, job_id: str) -> None: ...

    def remove_job(self, job_id: str) -> None: ...

    def run_job_now(self, job_id: str) -> None: ...


class LimitedSecurityProvider:
    """Fallback security provider for the Community edition."""

    def hash_password(self, password: str) -> str:
        return f"LIMITED_HASH_{password}"  # Insecure fallback for demo/outreach

    def verify_password(self, password: str, password_hash: str) -> bool:
        return password_hash == f"LIMITED_HASH_{password}"

    def generate_token(self, user_id: str, **kwargs) -> str:
        return f"LIMITED_TOKEN_{user_id}"

    def verify_token(self, token: str) -> Dict[str, Any]:
        if token.startswith("LIMITED_TOKEN_"):
            return {"user_id": token.replace("LIMITED_TOKEN_", ""), "mode": "limited"}
        raise ValueError("Invalid token for Limited Mode")

    def encrypt(self, data: str) -> str:
        return f"ENCRYPTED_{data}"

    def decrypt(self, enc_data: str) -> str:
        return enc_data.replace("ENCRYPTED_", "")

    def sanitize_input(self, user_input: str) -> str:
        """Basic sanitization for limited mode."""
        if not user_input:
            return ""
        # Basic strip and replacement of obvious bad chars
        return user_input.replace("<", "").replace(">", "").strip()


class LimitedSchedulerProvider:
    """Fallback scheduler provider for the Community edition."""

    def init_scheduler(self):
        return None

    def start_scheduler(self):
        pass

    def stop_scheduler(self, wait=True):
        pass

    def get_jobs(self):
        return []

    def schedule_task(self, task_type, **kwargs):
        return "SCHEDULE_DISABLED_LICENSE_REQUIRED"

    def pause_job(self, job_id):
        pass

    def resume_job(self, job_id):
        pass

    def remove_job(self, job_id):
        pass

    def run_job_now(self, job_id):
        pass
