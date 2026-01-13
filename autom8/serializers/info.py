# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""
System Info Serializer
"""


def serialize_system_info(
    app_name, version, environment, is_licensed, integrity_status, security_config, doc_url
):
    """Serialize system information."""
    return {
        "name": app_name,
        "version": version,
        "environment": environment,
        "licensed": is_licensed,
        "integrity": "verified" if integrity_status else "compromised",
        "security": {
            "rate_limiting": security_config.get("rate_limiting", False),
            "cors_enabled": security_config.get("cors_enabled", True),
            "https_only": security_config.get("https_only", False),
        },
        "documentation": doc_url,
    }


def serialize_health_check(status, service, version, environment):
    """
    Serialize simple health check response.
    """
    return {
        "status": status,
        "service": service,
        "version": version,
        "environment": environment,
    }


__all__ = ["serialize_system_info", "serialize_health_check"]
