# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""

Generate secure random keys for application configuration.
"""

import secrets
from cryptography.fernet import Fernet

print("=" * 70)
print("SECURE KEY GENERATOR")
print("=" * 70)
print("COPY THESE KEYS TO YOUR .env FILE")
print("=" * 70)

print("\n# Flask Secret Key (32 bytes)")
print(f"SECRET_KEY={secrets.token_urlsafe(32)}")

print("\n# JWT Secret Key (32 bytes)")
print(f"JWT_SECRET_KEY={secrets.token_urlsafe(32)}")

print("\n# Password Salt (16 bytes)")
print(f"PASSWORD_SALT={secrets.token_urlsafe(16)}")

print("\n# Encryption Key (Fernet)")
print(f"ENCRYPTION_KEY={Fernet.generate_key().decode()}")

print("\n# API KEY (for external services)")
print(f"API_KEY={secrets.token_urlsafe(32)}")

# Generate Autom8 Pro License Key
import hashlib
from datetime import datetime

def generate_license_key():
    """Generate a unique Autom8 Pro License Key."""
    # Timestamp component
    timestamp = datetime.now().strftime("%Y%m%d")
    # Random component (8 chars)
    random_part = secrets.token_hex(4).upper()
    # Signature component (checksum for validation)
    signature_data = f"ALO-PRO-{timestamp}-{random_part}"
    checksum = hashlib.sha256(signature_data.encode()).hexdigest()[:6].upper()
    
    return f"ALO-PRO-{timestamp}-{random_part}-{checksum}"

license_key = generate_license_key()
print("\n# Autom8 Pro License Key (enables Pro features)")
print(f"AUTOM8_LICENSE_KEY={license_key}")

print("\n" + "=" * 70)
print(" KEYS GENERATED SUCCESSFULLY ")
print(" Copy and paste them into your .env file ")
print(" Never share these keys publicly! ")
print(" Never commit your .env file to version control! ")
print("=" * 70 + "\n")
