# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""
config_validator.py - Configuration Validation

Validates all required environment variables at application startup.
Provides clear error messages if critical configuration is missing or invalid.
"""

import os
import sys
from typing import List, Tuple

from cryptography.fernet import Fernet

from autom8.core import log


class ConfigValidator:
    """Validate environment configuration before application startup."""

    # Critical variables that MUST be set in production
    CRITICAL_VARS = {
        "SECRET_KEY": {
            "min_length": 32,
            "description": "Flask secret key for session management",
            "example": "openssl rand -hex 32",
        },
        "JWT_SECRET_KEY": {
            "min_length": 32,
            "description": "JWT signing key",
            "example": "openssl rand -hex 32",
        },
        "PASSWORD_SALT": {
            "min_length": 32,
            "description": "Password hashing salt",
            "example": "openssl rand -hex 32",
        },
        "ENCRYPTION_KEY": {
            "type": "fernet",
            "description": "Fernet encryption key for sensitive data",
            "example": (
                "python -c 'from cryptography.fernet import Fernet; "
                "print(Fernet.generate_key().decode())'"
            ),
        },
    }

    # Variables with specific format requirements
    FORMAT_VALIDATORS = {
        "JWT_ALGORITHM": {
            "allowed": ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"],
            "description": "JWT algorithm must be one of: HS256, HS384, HS512, RS256, RS384, RS512",
        },
        "ENVIRONMENT": {
            "allowed": ["development", "staging", "production"],
            "description": "Environment must be one of: development, staging, production",
        },
    }

    @staticmethod
    def _validate_critical_vars() -> List[str]:
        """Check that all critical variables are set."""
        errors = []

        for var_name, config in ConfigValidator.CRITICAL_VARS.items():
            value = os.getenv(var_name)

            if not value:
                error_msg = (
                    f"CRITICAL: Missing required environment variable: {var_name}\n"
                    f"  Description: {config['description']}\n"
                    f"  To generate: {config['example']}"
                )
                errors.append(error_msg)

        return errors

    @staticmethod
    def _validate_variable_lengths(environment: str) -> List[str]:
        """Validate minimum length requirements for critical variables."""
        errors = []

        for var_name, config in ConfigValidator.CRITICAL_VARS.items():
            if "min_length" not in config:
                continue

            value = os.getenv(var_name)
            if not value:
                continue

            min_len = config["min_length"]
            if len(value) < min_len:
                errors.append(
                    f"INVALID: {var_name} must be at least {min_len} characters "
                    f"(currently {len(value)} chars)"
                )

        return errors

    @staticmethod
    def _validate_format_vars() -> List[str]:
        """Validate format of specific variables."""
        errors = []

        for var_name, config in ConfigValidator.FORMAT_VALIDATORS.items():
            value = os.getenv(var_name)
            if not value:
                continue

            if "allowed" in config:
                if value not in config["allowed"]:
                    errors.append(f"INVALID: {var_name} = '{value}'\n" f"  {config['description']}")

        return errors

    @staticmethod
    def _validate_fernet_key() -> List[str]:
        """Validate that ENCRYPTION_KEY is a valid Fernet key."""
        errors = []
        key = os.getenv("ENCRYPTION_KEY")

        if not key:
            return errors

        try:
            Fernet(key.encode())
        except Exception as e:
            errors.append(
                f"INVALID: ENCRYPTION_KEY is not a valid Fernet key\n"
                f"  Error: {str(e)}\n"
                f"  To generate: python -c "
                "'from cryptography.fernet import Fernet; "
                "print(Fernet.generate_key().decode())'"
            )

        return errors

    @staticmethod
    def validate_startup(environment: str = None) -> Tuple[bool, List[str]]:
        from autom8.config import Config

        errors = []
        env = environment or Config.ENVIRONMENT

        # Only enforce critical vars
        if env in ("production", "staging", "development"):
            errors.extend(ConfigValidator._validate_critical_vars())

        # Validate format of specific variables
        errors.extend(ConfigValidator._validate_format_vars())

        # Validate variable lengths
        errors.extend(ConfigValidator._validate_variable_lengths(env))

        # Validate Fernet key if present
        if os.getenv("ENCRYPTION_KEY"):
            errors.extend(ConfigValidator._validate_fernet_key())

        return len(errors) == 0, errors
    
    @staticmethod
    def validate_and_exit_if_invalid(environment: str = None) -> None:
        """Validate configuration and exit if invalid."""
        is_valid, errors = ConfigValidator.validate_startup(environment)

        if not is_valid:
            print("\n" + "=" * 70, file=sys.stderr)
            print("CONFIGURATION VALIDATION FAILED", file=sys.stderr)
            print("=" * 70, file=sys.stderr)

            for error in errors:
                print(f"\n❌ {error}", file=sys.stderr)

            print("\n" + "=" * 70, file=sys.stderr)
            print("Please set the required environment variables and try again.", file=sys.stderr)
            print("=" * 70 + "\n", file=sys.stderr)

            log.critical("Configuration validation failed. Application cannot start.")
            sys.exit(1)

    @staticmethod
    def print_config_summary() -> None:
        """Print a summary of current configuration (for debugging)."""
        from autom8.config import Config

        print("\n" + "=" * 70)
        print("CONFIGURATION SUMMARY")
        print("=" * 70)

        print("\nApplication Settings:")
        print(f"  APP_NAME: {Config.APP_NAME}")
        print(f"  APP_VERSION: {Config.APP_VERSION}")
        print(f"  ENVIRONMENT: {Config.ENVIRONMENT}")
        print(f"  DEBUG: {Config.DEBUG}")

        print("\nAPI Settings:")
        print(f"  API_HOST: {Config.API_HOST}")
        print(f"  API_PORT: {Config.API_PORT}")

        print("\nDatabase Settings:")
        print(f"  DATABASE_URL: {Config.DATABASE_URL}")
        print(f"  DB_ECHO: {Config.DB_ECHO}")

        print("\nLogging Settings:")
        print(f"  LOG_LEVEL: {Config.LOG_LEVEL}")

        print("\nScheduling Settings:")
        print(f"  BACKUP_INTERVAL_HOURS: {Config.BACKUP_INTERVAL_HOURS}")
        print(f"  REPORT_CRON_EXPRESSION: {Config.REPORT_CRON_EXPRESSION}")

        print("\nLicensing Settings:")
        print(f"  LICENSE_MODE: {Config.LICENSE_MODE}")
        print(f"  ENABLE_PRO: {Config.ENABLE_PRO}")

        print("\n" + "=" * 70 + "\n")


# Convenience function for easy importing
def validate_config() -> None:
    """Validate configuration at startup. Exit if invalid."""
    ConfigValidator.validate_and_exit_if_invalid()


__all__ = ["ConfigValidator", "validate_config"]
