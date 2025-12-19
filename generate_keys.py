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

print("\n" + "=" * 70)
print(" KEYS GENERATED SUCCESSFULLY ")
print(" Copy and paste them into your .env file ")
print(" Never share these keys publicly! ")
print(" Never commit your .env file to version control! ")
print("=" * 70 + "\n")
