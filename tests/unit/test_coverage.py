# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.

"""
Coverage boost tests.
"""

from unittest.mock import patch
from autom8 import api


def test_api_error_handlers(client):
    """Test API error handlers."""
    # 400 Bad Request
    with patch("autom8.api.validate_contact_data", return_value=(False, "Bad")):
        client.post("/api/v1/contacts", json={})
        # Depending on implementation, it might trigger 400 handler via abort(400)

    # 401 Unauthorized
    # 403 Forbidden
    # We can invoke handlers directly to ensure coverage
    with api.app.app_context():
        from werkzeug.exceptions import BadRequest, Unauthorized, Forbidden

        resp, code = api.bad_request(BadRequest("Test"))
        assert code == 400

        resp, code = api.unauthorized_handler(Unauthorized("Test"))
        assert code == 401

        resp, code = api.forbidden_handler(Forbidden("Test"))
        assert code == 403


def test_security_validation_edges():
    from autom8.security import validate_email, validate_phone

    assert validate_email("test@example.com") is True
    assert validate_email("invalid") is False

    assert validate_phone("0712345678") is True
    assert validate_phone("123") is False
