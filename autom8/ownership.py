# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
"""
ownership.py - Ownership Management Module
"""
import base64
import hashlib
import json
from datetime import datetime, timezone

from autom8.config import Config


class OwnershipAuthority:
    @staticmethod
    def is_licensed() -> bool:
        """Check if license is valid and not expired"""
        signature = Config.PROTECT_SIGNATURE

        # Basic validation
        if not signature or len(signature) < 16:
            return False

        try:
            # Decode license data
            decoded = base64.b64decode(signature)
            data = json.loads(decoded)

            # Validate required fields
            required_fields = ["customer_id", "expires", "signature"]
            if not all(field in data for field in required_fields):
                return False

            # Check expiration with timezone awareness
            expires_dt = datetime.fromisoformat(data["expires"]).replace(tzinfo=timezone.utc)
            current_time = datetime.now(timezone.utc)

            if current_time > expires_dt:
                return False

            # Verify signature integrity
            expected_hash = hashlib.sha256(
                f"{data['customer_id']}:{data['expires']}".encode()
            ).hexdigest()

            if data["signature"] != expected_hash:
                return False

            return True

        except (json.JSONDecodeError, ValueError, KeyError, TypeError, AttributeError):
            return False

    @staticmethod
    def integrity_token() -> str:
        base = Config.PROTECT_SIGNATURE.encode()
        return hashlib.sha256(base).hexdigest()[:12]

    @staticmethod
    def integrity_verified() -> bool:
        return OwnershipAuthority.is_licensed()
