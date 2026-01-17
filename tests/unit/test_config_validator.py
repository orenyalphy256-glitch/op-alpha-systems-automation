# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""
test_config_validator.py - Configuration Validator Tests

Tests for environment configuration validation at startup.
"""

import os
from unittest.mock import patch

import pytest
from cryptography.fernet import Fernet

from autom8.config_validator import ConfigValidator


class TestConfigValidatorCriticalVars:
    """Test validation of critical environment variables."""

    def test_validate_startup_all_critical_vars_missing(self):
        """Test validation fails when all critical vars are missing."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("autom8.config.Config.ENVIRONMENT", "production"):
                is_valid, errors = ConfigValidator.validate_startup("production")

        assert not is_valid
        assert len(errors) >= 4  # At least 4 critical vars
        error_text = "\n".join(errors)
        assert "SECRET_KEY" in error_text
        assert "JWT_SECRET_KEY" in error_text
        assert "PASSWORD_SALT" in error_text
        assert "ENCRYPTION_KEY" in error_text

    def test_validate_startup_development_skips_critical_check(self):
        """Test that development environment doesn't enforce critical vars."""
        with patch.dict(os.environ, {}, clear=True):
            is_valid, errors = ConfigValidator.validate_startup("development")

        # In dev mode, missing critical vars are not enforced
        critical_errors = [e for e in errors if "CRITICAL" in e]
        assert len(critical_errors) == 0

    def test_validate_startup_staging_enforces_critical(self):
        """Test that staging environment enforces critical variables."""
        with patch.dict(os.environ, {}, clear=True):
            is_valid, errors = ConfigValidator.validate_startup("staging")

        assert not is_valid
        critical_errors = [e for e in errors if "CRITICAL" in e]
        assert len(critical_errors) >= 4

    def test_validate_startup_with_valid_critical_vars(self):
        """Test validation passes with valid critical variables."""
        valid_key = "a" * 32
        valid_fernet = Fernet.generate_key().decode()

        env_vars = {
            "SECRET_KEY": valid_key,
            "JWT_SECRET_KEY": valid_key,
            "PASSWORD_SALT": valid_key,
            "ENCRYPTION_KEY": valid_fernet,
            "ENVIRONMENT": "production",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            is_valid, errors = ConfigValidator.validate_startup("production")

        assert is_valid
        assert len(errors) == 0


class TestConfigValidatorVariableLengths:
    """Test validation of variable minimum lengths."""

    def test_secret_key_too_short(self):
        """Test validation fails when SECRET_KEY is too short."""
        env_vars = {
            "SECRET_KEY": "short",
            "ENVIRONMENT": "production",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            is_valid, errors = ConfigValidator.validate_startup("production")

        assert not is_valid
        length_errors = [e for e in errors if "at least 32 characters" in e]
        assert len(length_errors) >= 1

    def test_jwt_secret_key_too_short(self):
        """Test validation fails when JWT_SECRET_KEY is too short."""
        env_vars = {
            "JWT_SECRET_KEY": "short",
            "ENVIRONMENT": "production",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            is_valid, errors = ConfigValidator.validate_startup("production")

        assert not is_valid
        length_errors = [e for e in errors if "JWT_SECRET_KEY" in e and "at least 32" in e]
        assert len(length_errors) >= 1

    def test_password_salt_too_short(self):
        """Test validation fails when PASSWORD_SALT is too short."""
        env_vars = {
            "PASSWORD_SALT": "short",
            "ENVIRONMENT": "production",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            is_valid, errors = ConfigValidator.validate_startup("production")

        assert not is_valid
        length_errors = [e for e in errors if "PASSWORD_SALT" in e and "at least 32" in e]
        assert len(length_errors) >= 1


class TestConfigValidatorFormatValidation:
    """Test validation of variable formats."""

    def test_invalid_jwt_algorithm(self):
        """Test validation fails with invalid JWT algorithm."""
        env_vars = {
            "JWT_ALGORITHM": "INVALID",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            is_valid, errors = ConfigValidator.validate_startup("development")

        assert not is_valid
        format_errors = [e for e in errors if "JWT_ALGORITHM" in e]
        assert len(format_errors) >= 1

    def test_valid_jwt_algorithms(self):
        """Test that valid JWT algorithms pass validation."""
        valid_algorithms = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]

        for algo in valid_algorithms:
            env_vars = {
                "JWT_ALGORITHM": algo,
            }

            with patch.dict(os.environ, env_vars, clear=True):
                is_valid, errors = ConfigValidator.validate_startup("development")

            algo_errors = [e for e in errors if "JWT_ALGORITHM" in e]
            assert len(algo_errors) == 0, f"Algorithm {algo} should be valid"

    def test_invalid_environment(self):
        """Test validation fails with invalid ENVIRONMENT."""
        env_vars = {
            "ENVIRONMENT": "invalid",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            is_valid, errors = ConfigValidator.validate_startup("invalid")

        assert not is_valid
        env_errors = [e for e in errors if "ENVIRONMENT" in e]
        assert len(env_errors) >= 1

    def test_valid_environments(self):
        """Test that valid environments pass validation."""
        valid_envs = ["development", "staging", "production"]

        for env in valid_envs:
            with patch.dict(os.environ, {"ENVIRONMENT": env}, clear=True):
                is_valid, errors = ConfigValidator.validate_startup(env)

            env_errors = [e for e in errors if "ENVIRONMENT" in e and "must be one of" in e]
            assert len(env_errors) == 0, f"Environment {env} should be valid"


class TestConfigValidatorFernetKey:
    """Test validation of Fernet encryption keys."""

    def test_invalid_fernet_key(self):
        """Test validation fails with invalid Fernet key."""
        env_vars = {
            "ENCRYPTION_KEY": "not-a-valid-fernet-key",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            is_valid, errors = ConfigValidator.validate_startup("development")

        assert not is_valid
        fernet_errors = [e for e in errors if "ENCRYPTION_KEY" in e and "Fernet" in e]
        assert len(fernet_errors) >= 1

    def test_valid_fernet_key(self):
        """Test validation passes with valid Fernet key."""
        valid_key = Fernet.generate_key().decode()
        env_vars = {
            "ENCRYPTION_KEY": valid_key,
        }

        with patch.dict(os.environ, env_vars, clear=True):
            is_valid, errors = ConfigValidator.validate_startup("development")

        fernet_errors = [e for e in errors if "ENCRYPTION_KEY" in e and "Fernet" in e]
        assert len(fernet_errors) == 0

    def test_missing_fernet_key_not_validated(self):
        """Test that missing Fernet key is not validated (only format if present)."""
        env_vars = {}

        with patch.dict(os.environ, env_vars, clear=True):
            is_valid, errors = ConfigValidator.validate_startup("development")

        # Missing key should not produce Fernet validation error
        fernet_errors = [e for e in errors if "ENCRYPTION_KEY" in e and "Fernet" in e]
        assert len(fernet_errors) == 0


class TestConfigValidatorCompleteSetup:
    """Test complete valid configuration setup."""

    def test_complete_production_setup(self):
        """Test validation passes with complete valid production setup."""
        valid_key = "a" * 32
        valid_fernet = Fernet.generate_key().decode()

        env_vars = {
            "APP_NAME": "Autom8",
            "APP_VERSION": "1.0.0",
            "ENVIRONMENT": "production",
            "DEBUG": "false",
            "SECRET_KEY": valid_key,
            "API_HOST": "127.0.0.1",
            "API_PORT": "5000",
            "TIMEZONE": "UTC",
            "DATABASE_URL": "sqlite:///data/system.db",
            "DB_ECHO": "false",
            "LICENSE_MODE": "community",
            "PROTECT_SIGNATURE": "base64-signature",
            "ENABLE_PRO": "false",
            "LOG_LEVEL": "INFO",
            "BACKUP_INTERVAL_HOURS": "24",
            "REPORT_CRON_EXPRESSION": "0 9 * * *",
            "JWT_SECRET_KEY": valid_key,
            "JWT_ALGORITHM": "HS256",
            "JWT_EXPIRATION_HOURS": "24",
            "PASSWORD_SALT": valid_key,
            "PASSWORD_MIN_LENGTH": "8",
            "ENCRYPTION_KEY": valid_fernet,
            "RATE_LIMIT_ENABLED": "true",
            "RATE_LIMIT_DEFAULT": "5000 per minute",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            is_valid, errors = ConfigValidator.validate_startup("production")

        assert is_valid
        assert len(errors) == 0


class TestConfigValidatorErrorMessages:
    """Test that error messages are helpful and informative."""

    def test_error_message_includes_description(self):
        """Test that error messages include variable description."""
        env_vars = {}

        with patch.dict(os.environ, env_vars, clear=True):
            is_valid, errors = ConfigValidator.validate_startup("production")

        assert not is_valid
        error_text = "\n".join(errors)

        # Check for helpful information in errors
        assert "Description:" in error_text or "description" in error_text

    def test_error_message_includes_generation_example(self):
        """Test that error messages include example of how to generate missing vars."""
        env_vars = {}

        with patch.dict(os.environ, env_vars, clear=True):
            is_valid, errors = ConfigValidator.validate_startup("production")

        assert not is_valid
        error_text = "\n".join(errors)

        # Check for examples (openssl, python, etc.)
        assert "openssl" in error_text or "python" in error_text or "generate" in error_text.lower()
