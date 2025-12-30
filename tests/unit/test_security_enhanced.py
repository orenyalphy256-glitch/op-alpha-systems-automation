# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.

import jwt
from unittest.mock import patch
from flask import Flask
from autom8 import security
from autom8.security import SecurityConfig, Encryptor


def test_verify_token_expired():
    # Create an expired token
    payload = {"user_id": "test_user", "exp": 0}
    token = jwt.encode(
        payload, SecurityConfig.JWT_SECRET_KEY, algorithm=SecurityConfig.JWT_ALGORITHM
    )

    with patch("autom8.security.log") as mock_log:
        result = security.verify_token(token)
        assert result is None
        mock_log.warning.assert_called_with("Token has expired")


def test_verify_token_invalid():
    with patch("autom8.security.log") as mock_log:
        result = security.verify_token("invalid.token.here")
        assert result is None
        mock_log.warning.assert_called_with("Invalid token")


def test_token_required_no_token():
    app = Flask(__name__)

    @app.route("/")
    @security.token_required
    def protected(payload):
        return "success"

    with app.test_request_context():
        response, code = protected()
        assert code == 401


def test_token_required_invalid_header_format():
    app = Flask(__name__)

    @app.route("/")
    @security.token_required
    def protected(payload):
        return "success"

    with app.test_request_context(headers={"Authorization": "Bearer"}):
        response, code = protected()
        assert code == 401


def test_get_rate_limit_key_x_forwarded_for():
    app = Flask(__name__)
    with app.test_request_context(headers={"X-Forwarded-For": "1.2.3.4, 5.6.7.8"}):
        key = security.get_rate_limit_key()
        assert key == "rate_limit:1.2.3.4"


def test_get_rate_limit_key_no_addr():
    app = Flask(__name__)
    with app.test_request_context():
        with patch("flask.request.remote_addr", None):
            key = security.get_rate_limit_key()
            assert key == "rate_limit:unknown"


def test_log_security_event_severities():
    with patch("autom8.security.log") as mock_log:
        security.log_security_event("test_info", {"foo": "bar"}, "INFO")
        mock_log.info.assert_called()

        security.log_security_event("test_warning", {"foo": "bar"}, "WARNING")
        mock_log.warning.assert_called()

        security.log_security_event("test_error", {"foo": "bar"}, "ERROR")
        mock_log.error.assert_called()


def test_encryptor_edge_cases():
    enc = Encryptor()
    # Empty data
    assert enc.encrypt("") == ""
    # Byte input
    data = "test_bytes"
    encrypted = enc.encrypt(data)
    decrypted = enc.decrypt(encrypted.encode())
    assert decrypted == data


def test_is_safe_url():
    app = Flask(__name__)
    with app.test_request_context(base_url="http://localhost"):
        assert security.is_safe_url("http://localhost/path") is True
        assert security.is_safe_url("https://malicious.com") is False
        assert security.is_safe_url("/local/path") is True


def test_security_validation_basics():
    assert security.validate_phone("invalid") is False
    assert security.validate_email("invalid") is False
    assert security.sanitize_input("") == ""
