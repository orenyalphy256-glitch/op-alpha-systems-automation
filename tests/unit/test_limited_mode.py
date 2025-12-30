# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.

"""
Unit tests for Limited Mode (Community Edition) functionality.
"""

from unittest.mock import patch
import pytest
from autom8 import interfaces
from autom8.core import get_security, get_scheduler, is_licensed, Config


def test_is_licensed_false():
    """Test that is_licensed returns False when key is missing or invalid."""
    with patch.object(Config, "LICENSE_KEY", "DEMO-COMMUNITY-MODE"):
        assert is_licensed() is False

    with patch.object(Config, "LICENSE_KEY", None):
        assert is_licensed() is False

    with patch.object(Config, "LICENSE_KEY", "INVALID-KEY"):
        assert is_licensed() is False


def test_limited_security_provider():
    """Test LimitedSecurityProvider fallback behavior."""
    # Force Limited Mode logic by mocking imports or ensuring fallback
    # We can directly instantiate LimitedSecurityProvider to test it
    provider = interfaces.LimitedSecurityProvider()

    assert provider.hash_password("password") == "LIMITED_HASH_password"
    assert provider.verify_password("password", "LIMITED_HASH_password") is True
    assert provider.verify_password("password", "wrong") is False

    token = provider.generate_token("user1")
    assert token == "LIMITED_TOKEN_user1"

    decoded = provider.verify_token(token)
    assert decoded["user_id"] == "user1"
    assert decoded["mode"] == "limited"

    with pytest.raises(ValueError):
        provider.verify_token("INVALID_TOKEN")

    assert provider.encrypt("data") == "ENCRYPTED_data"
    assert provider.decrypt("ENCRYPTED_data") == "data"
    assert provider.sanitize_input("<bad>") == "bad"


def test_limited_scheduler_provider():
    """Test LimitedSchedulerProvider fallback behavior."""
    provider = interfaces.LimitedSchedulerProvider()

    assert provider.init_scheduler() is None
    assert provider.get_jobs() == []
    assert provider.schedule_task("test") == "SCHEDULE_DISABLED_LICENSE_REQUIRED"

    # These should do nothing (void methods)
    provider.start_scheduler()
    provider.stop_scheduler()
    provider.pause_job("j1")
    provider.resume_job("j1")
    provider.remove_job("j1")
    provider.run_job_now("j1")


@patch("autom8.core._security_provider", None)
@patch("autom8.core._scheduler_provider", None)
def test_fallback_mechanism():
    """Test that core.py falls back to Limited providers when Import fails."""
    # Mock Config.LICENSE_KEY to avoid trying to load core engine
    with patch.object(Config, "LICENSE_KEY", "DEMO-COMMUNITY-MODE"):

        # Test get_security logic
        # We need to simulate that interfaces ARE available but core is not auto-loaded
        # (Auto-creation of LimitedProvider happens inside get_security fallback)

        # Ensure imports succeed
        with patch.dict("sys.modules"):
            sec = get_security()
            assert isinstance(sec, interfaces.LimitedSecurityProvider)

            sched = get_scheduler()
            assert isinstance(sched, interfaces.LimitedSchedulerProvider)
