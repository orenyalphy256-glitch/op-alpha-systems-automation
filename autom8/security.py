"""
Security-related utilities for the autom8 package.
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Dict, Any

from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import jwt

from autom8.core import log


# CONFIGURATION
class SecurityConfig:
    """Security configuration from environment variables."""

    # JWT settings
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "dev-secret-key-change-in-production",
    )
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

    # Password settings
    PASSWORD_SALT = os.getenv(
        "PASSWORD_SALT",
        "default-salt-change-in-production",
    )
    PASSWORD_MIN_LENGTH = 8

    # Rate limiting
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "True") == "True"
    RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "100 per hour")

    # Encryption
    ENCRYPTION_KEY = os.getenv(
        "ENCRYPTION_KEY",
        Fernet.generate_key().decode(),
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

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt an encrypted string."""
        if not encrypted_data:
            return ""

        decrypted_bytes = self.cipher.decrypt(encrypted_data.encode())
        return decrypted_bytes.decode()


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
    """Generate a secure random API key."""
    return secrets.token_urlsafe(32)


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
    from urllib.parse import urlparse, urljoin

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
