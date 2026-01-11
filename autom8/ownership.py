# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
"""
ownership.py - Ownership Management Module
"""
import hashlib
from autom8.config import Config


class OwnershipAuthority:
    @staticmethod
    def is_licensed() -> bool:
        signature = Config.PROTECT_SIGNATURE
        return bool(signature and len(signature) >= 16)

    @staticmethod
    def integrity_token() -> str:
        base = Config.PROTECT_SIGNATURE.encode()
        return hashlib.sha256(base).hexdigest()[:12]

    @staticmethod
    def integrity_verified() -> bool:
        return OwnershipAuthority.is_licensed()
