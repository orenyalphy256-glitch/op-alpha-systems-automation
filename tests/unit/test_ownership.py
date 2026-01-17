# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""
Tests for autom8/ownership.py

Comprehensive test suite for the OwnershipAuthority module.
"""

import base64
import hashlib
import json
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch

from autom8.ownership import OwnershipAuthority


class TestOwnershipAuthority:
    """Test OwnershipAuthority class"""

    def _create_valid_license(self, expires_in_days=30):
        """Helper to create a valid license signature"""
        customer_id = "test_customer"
        expires = (
            datetime.now(timezone.utc) + timedelta(days=expires_in_days)
        ).isoformat()

        expected_hash = hashlib.sha256(
            f"{customer_id}:{expires}".encode()
        ).hexdigest()

        data = {
            "customer_id": customer_id,
            "expires": expires,
            "signature": expected_hash
        }

        encoded = base64.b64encode(
            json.dumps(data).encode()
        ).decode()
        return encoded

    def _create_expired_license(self):
        """Helper to create an expired license signature"""
        customer_id = "test_customer"
        expires = (
            datetime.now(timezone.utc) - timedelta(days=1)
        ).isoformat()

        expected_hash = hashlib.sha256(
            f"{customer_id}:{expires}".encode()
        ).hexdigest()

        data = {
            "customer_id": customer_id,
            "expires": expires,
            "signature": expected_hash
        }

        encoded = base64.b64encode(
            json.dumps(data).encode()
        ).decode()
        return encoded

    @patch("autom8.ownership.Config.PROTECT_SIGNATURE", "")
    def test_is_licensed_empty_signature(self):
        """Test is_licensed with empty signature"""
        assert OwnershipAuthority.is_licensed() is False

    @patch("autom8.ownership.Config.PROTECT_SIGNATURE", "short")
    def test_is_licensed_short_signature(self):
        """Test is_licensed with short signature"""
        assert OwnershipAuthority.is_licensed() is False

    @patch("autom8.ownership.Config")
    def test_is_licensed_valid_license(self, mock_config):
        """Test is_licensed with valid license"""
        mock_config.PROTECT_SIGNATURE = self._create_valid_license()

        assert OwnershipAuthority.is_licensed() is True

    @patch("autom8.ownership.Config.PROTECT_SIGNATURE")
    def test_is_licensed_expired_license(self, mock_sig):
        """Test is_licensed with expired license"""
        mock_sig.return_value = self._create_expired_license()

        assert OwnershipAuthority.is_licensed() is False

    @patch("autom8.ownership.Config.PROTECT_SIGNATURE")
    def test_is_licensed_invalid_base64(self, mock_sig):
        """Test is_licensed with invalid base64"""
        mock_sig.return_value = "not_valid_base64!!!"

        assert OwnershipAuthority.is_licensed() is False

    @patch("autom8.ownership.Config.PROTECT_SIGNATURE")
    def test_is_licensed_invalid_json(self, mock_sig):
        """Test is_licensed with invalid JSON"""
        invalid_json = base64.b64encode(b"not json").decode()
        mock_sig.return_value = invalid_json

        assert OwnershipAuthority.is_licensed() is False

    @patch("autom8.ownership.Config.PROTECT_SIGNATURE")
    def test_is_licensed_missing_customer_id(self, mock_sig):
        """Test is_licensed with missing customer_id field"""
        data = {
            "expires": datetime.now(timezone.utc).isoformat(),
            "signature": "some_hash"
        }
        encoded = base64.b64encode(json.dumps(data).encode()).decode()
        mock_sig.return_value = encoded

        assert OwnershipAuthority.is_licensed() is False

    @patch("autom8.ownership.Config.PROTECT_SIGNATURE")
    def test_is_licensed_missing_expires(self, mock_sig):
        """Test is_licensed with missing expires field"""
        data = {
            "customer_id": "test_customer",
            "signature": "some_hash"
        }
        encoded = base64.b64encode(json.dumps(data).encode()).decode()
        mock_sig.return_value = encoded

        assert OwnershipAuthority.is_licensed() is False

    @patch("autom8.ownership.Config.PROTECT_SIGNATURE")
    def test_is_licensed_missing_signature(self, mock_sig):
        """Test is_licensed with missing signature field"""
        data = {
            "customer_id": "test_customer",
            "expires": datetime.now(timezone.utc).isoformat(),
        }
        encoded = base64.b64encode(json.dumps(data).encode()).decode()
        mock_sig.return_value = encoded

        assert OwnershipAuthority.is_licensed() is False

    @patch("autom8.ownership.Config.PROTECT_SIGNATURE")
    def test_is_licensed_invalid_signature(self, mock_sig):
        """Test is_licensed with invalid signature hash"""
        customer_id = "test_customer"
        expires = datetime.now(timezone.utc).isoformat()
        wrong_hash = "0" * 64  # Invalid hash

        data = {
            "customer_id": customer_id,
            "expires": expires,
            "signature": wrong_hash
        }
        encoded = base64.b64encode(json.dumps(data).encode()).decode()
        mock_sig.return_value = encoded

        assert OwnershipAuthority.is_licensed() is False

    @patch("autom8.ownership.Config.PROTECT_SIGNATURE")
    def test_is_licensed_invalid_datetime_format(self, mock_sig):
        """Test is_licensed with invalid datetime format"""
        data = {
            "customer_id": "test_customer",
            "expires": "not-a-valid-datetime",
            "signature": "some_hash"
        }
        encoded = base64.b64encode(json.dumps(data).encode()).decode()
        mock_sig.return_value = encoded

        assert OwnershipAuthority.is_licensed() is False

    @patch("autom8.ownership.Config")
    def test_integrity_token(self, mock_config):
        """Test integrity_token generation"""
        mock_config.PROTECT_SIGNATURE = self._create_valid_license()

        token = OwnershipAuthority.integrity_token()
        assert token is not None
        assert len(token) == 12
        assert isinstance(token, str)

    @patch("autom8.ownership.Config")
    def test_integrity_verified_valid(self, mock_config):
        """Test integrity_verified with valid license"""
        mock_config.PROTECT_SIGNATURE = self._create_valid_license()

        assert OwnershipAuthority.integrity_verified() is True

    @patch("autom8.ownership.Config.PROTECT_SIGNATURE")
    def test_integrity_verified_expired(self, mock_sig):
        """Test integrity_verified with expired license"""
        mock_sig.return_value = self._create_expired_license()

        assert OwnershipAuthority.integrity_verified() is False

    @patch("autom8.ownership.Config.PROTECT_SIGNATURE")
    def test_integrity_verified_invalid(self, mock_sig):
        """Test integrity_verified with invalid license"""
        mock_sig.return_value = "invalid_signature"

        assert OwnershipAuthority.integrity_verified() is False
