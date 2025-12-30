# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.

import pytest
from autom8 import interfaces

def test_limited_security_provider_verify_token_error():
    provider = interfaces.LimitedSecurityProvider()
    with pytest.raises(ValueError, match="Invalid token for Limited Mode"):
        provider.verify_token("WRONG_TOKEN")

def test_limited_scheduler_provider_stubs():
    provider = interfaces.LimitedSchedulerProvider()
    # Ensure they return what they should or None for void
    assert provider.init_scheduler() is None
    assert provider.start_scheduler() is None
    assert provider.stop_scheduler() is None
    assert provider.get_jobs() == []
    assert provider.pause_job("1") is None
    assert provider.resume_job("1") is None
    assert provider.remove_job("1") is None
    assert provider.run_job_now("1") is None

def test_limited_security_provider_sanitize_empty():
    provider = interfaces.LimitedSecurityProvider()
    assert provider.sanitize_input("") == ""
    assert provider.sanitize_input(None) == ""
