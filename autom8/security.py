# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""

Security-related utilities for the autom8 package.
"""

import hashlib
import os
import secrets
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, Optional

import jwt
from cryptography.fernet import Fernet
from flask import jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from autom8.core import log, Config

# Stealth entropy key for proprietary verification
_PROTECTION_ID = Config.PROTECT_SIGNATURE


# CONFIGURATION
class SecurityConfig:
    """Security configuration from environment variables."""

    # JWT settings
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY"
    )
    if not JWT_SECRET_KEY:
        raise ValueError(
            "JWT_SECRET_KEY environment variable is required"
        )
    if len(JWT_SECRET_KEY) < 32:
        raise ValueError(
            "JWT_SECRET_KEY environment variable must be at least 32 characters long"
        )
    
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

    # Password settings
    PASSWORD_SALT = os.getenv(
        "PASSWORD_SALT"
    )
    if not PASSWORD_SALT:
        raise ValueError(
            "PASSWORD_SALT environment variable is required"
        )
    if len(PASSWORD_SALT) < 32:
        raise ValueError(
            "PASSWORD_SALT environment variable must be at least 32 characters long"
        )
    
    PASSWORD_MIN_LENGTH = os.getenv("PASSWORD_MIN_LENGTH")

    # Rate limiting (Boolean check)
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"

    # Rate limit values (with safe defaults)
    RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "5000 per minute")
    RATE_LIMIT_CONTACTS_GET = os.getenv("RATE_LIMIT_CONTACTS_GET", "5000 per minute")
    RATE_LIMIT_CONTACTS_POST = os.getenv("RATE_LIMIT_CONTACTS_POST", "5000 per minute")
    RATE_LIMIT_CONTACTS_PUT = os.getenv("RATE_LIMIT_CONTACTS_PUT", "4000 per minute")
    RATE_LIMIT_CONTACTS_DELETE = os.getenv("RATE_LIMIT_CONTACTS_DELETE", "3000 per minute")

    # Storage backend for rate limiting
    RATE_LIMIT_STORAGE = os.getenv("RATE_LIMIT_STORAGE", "memory://")

    # Encryption
    ENCRYPTION_KEY = os.getenv(
        "ENCRYPTION_KEY"
    )
    if not ENCRYPTION_KEY:
        raise ValueError(
            "ENCRYPTION_KEY environment variable is required"
        )
    
    # Validate Fernet key format
    try:
        Fernet(ENCRYPTION_KEY.encode())
    except Exception as e:
        raise ValueError(
            "ENCRYPTION_KEY environment variable is invalid"
        )

    # Security Headers
    SECURITY_HEADERS = {
        "Content-Security-Policy": "default-src 'self'",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "same-origin",
        "Permissions-Policy": ("geolocation=(), camera=(), microphone=(), payment=()"),
    }


# PASSWORD HASHING
def hash_password(password: str) -> str:
    """Hash a password using werkzeug's secure method."""
    if not password or len(password) < SecurityConfig.PASSWORD_MIN_LENGTH:
        raise ValueError(
            f"Password must be at least " f"{SecurityConfig.PASSWORD_MIN_LENGTH} characters long"
        )

    return generate_password_hash(
        password,
        method="pbkdf2:sha256",
        salt_length=16,
    )


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    return check_password_hash(password_hash, password)


# JWT TOKENS
def generate_token(
    user_id: str,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Generate a JWT token for authentication."""
    expiration = datetime.now() + timedelta(hours=SecurityConfig.JWT_EXPIRATION_HOURS)

    payload = {
        "user_id": user_id,
        "exp": expiration,
        "iat": datetime.now(),
        "jti": secrets.token_urlsafe(16),
    }

    if additional_claims:
        payload.update(additional_claims)

    token = jwt.encode(
        payload,
        SecurityConfig.JWT_SECRET_KEY,
        algorithm=SecurityConfig.JWT_ALGORITHM,
    )

    log.info(f"Token generated for user: {user_id}")
    return token


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(
            token,
            SecurityConfig.JWT_SECRET_KEY,
            algorithms=[SecurityConfig.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        log.warning("Token has expired")
        return None
    except jwt.InvalidTokenError:
        log.warning("Invalid token")
        return None


def token_required(f):
    """Decorator to require valid JWT token for endpoint."""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                pass

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        payload = verify_token(token)
        if not payload:
            return jsonify({"error": "Token is invalid or expired"}), 401

        return f(payload, *args, **kwargs)

    return decorated


# ENCRYPTION
class Encryptor:
    """Handle encryption and decryption of sensitive data."""

    def __init__(self):
        """Initialize encryptor with key from environment."""
        key = SecurityConfig.ENCRYPTION_KEY

        if isinstance(key, str):
            key = key.encode()

        self.cipher = Fernet(key)

    def encrypt(self, data: str) -> str:
        """Encrypt a string."""
        if not data:
            return ""

        encrypted_bytes = self.cipher.encrypt(data.encode())
        return encrypted_bytes.decode()

    def decrypt(self, encrypted_data: str):
        """Decrypt an encrypted string."""
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode()
        return self.cipher.decrypt(encrypted_data).decode()


# Global encryptor instance
encryptor = Encryptor()


# INPUT VALIDATION
def sanitize_input(
    user_input: str,
    max_length: int = 255,
) -> str:
    """Sanitize user input to prevent injection attacks."""
    if not user_input:
        return ""

    sanitized = user_input[:max_length]
    sanitized = sanitized.replace("\x00", "")
    sanitized = sanitized.strip()
    sanitized = (
        sanitized.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )

    return sanitized


def validate_phone(phone: str) -> bool:
    import re

    patterns = [
        r"^07\d{8}$",
        r"^\+2547\d{8}$",
        r"^2547\d{8}$",
        r"^01\d{8}$",
        r"^\+2541\d{8}$",
    ]

    for pattern in patterns:
        if re.match(pattern, phone):
            return True

    return False


def validate_email(email: str) -> bool:
    import re

    pattern = r"^[a-zA-Z0-9._%+-]+@" r"[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


# SECURITY HEADERS
def add_security_headers(response):
    """Add security headers to Flask response."""
    for header, value in SecurityConfig.SECURITY_HEADERS.items():
        response.headers[header] = value

    return response


# API KEY MANAGEMENT
def generate_api_key() -> str:
    """Generate a secure random API key with proprietary salt."""
    # Salted with internal protection ID
    return secrets.token_urlsafe(32) + f".{_PROTECTION_ID[:8]}"


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(api_key: str, stored_hash: str) -> bool:
    """Verify an API key against its hash."""
    return hash_api_key(api_key) == stored_hash


# RATE LIMITING HELPERS
def get_rate_limit_key() -> str:
    """Get rate limit key based on request."""
    if request.headers.get("X-Forwarded-For"):
        ip = request.headers.get("X-Forwarded-For").split(",")[0].strip()
    else:
        ip = request.remote_addr or "unknown"

    return f"rate_limit:{ip}"


# AUDIT LOGGING
def log_security_event(
    event_type: str,
    details: Dict[str, Any],
    severity: str = "INFO",
):
    """Log security event to audit log."""
    log_message = f"Security Event: {event_type} | {details}"

    if severity == "WARNING":
        log.warning(log_message)
    elif severity == "ERROR":
        log.error(log_message)
    else:
        log.info(log_message)


# UTILITY FUNCTIONS
def is_safe_url(target: str) -> bool:
    """Check if a URL is safe for redirection."""
    from urllib.parse import urljoin, urlparse

    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))

    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def generate_random_string(length: int = 32) -> str:
    """Generate cryptographically secure random string."""
    return secrets.token_urlsafe(length)[:length]


# EXPORTS
__all__ = [
    "SecurityConfig",
    "hash_password",
    "verify_password",
    "generate_token",
    "verify_token",
    "token_required",
    "Encryptor",
    "encryptor",
    "sanitize_input",
    "validate_phone",
    "validate_email",
    "add_security_headers",
    "generate_api_key",
    "hash_api_key",
    "verify_api_key",
    "get_rate_limit_key",
    "log_security_event",
    "is_safe_url",
    "generate_random_string",
]
