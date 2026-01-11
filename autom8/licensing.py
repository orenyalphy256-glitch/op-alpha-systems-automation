# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
"""
licensing.py - Licensing Management Module
"""
from autom8.ownership import OwnershipAuthority


def is_licensed() -> bool:
    return OwnershipAuthority.is_licensed()


def integrity_token() -> str:
    return OwnershipAuthority.integrity_token()
