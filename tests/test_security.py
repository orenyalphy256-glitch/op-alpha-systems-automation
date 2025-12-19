"""
Security Testing Script
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

from autom8.security import (
    hash_password,
    verify_password,
    generate_token,
    verify_token,
    encryptor,
    sanitize_input,
    validate_phone,
    validate_email,
    generate_api_key,
    hash_api_key,
    verify_api_key,
)


def test_password_hashing():
    """Test password hashing."""
    print("\n" + "=" * 70)
    print("TEST 1: Password Hashing")
    print("=" * 70)

    password = "MySecurePassword123!"
    print(f"Original password: {password}")

    # Hash password
    hashed = hash_password(password)
    print(f"Hashed: {hashed[:50]}...")

    # Verify correct password
    is_valid = verify_password(password, hashed)
    print(f"Correct password verification: {is_valid}")
    assert is_valid, "Password verification failed!"

    # Verify wrong password
    is_invalid = verify_password("WrongPassword", hashed)
    print(f"Wrong password verification: {is_invalid}")
    assert not is_invalid, "Wrong password should not verify!"

    print("✅ Password hashing: PASSED")


def test_jwt_tokens():
    """Test JWT token generation and verification."""
    print("\n" + "=" * 70)
    print("TEST 2: JWT Tokens")
    print("=" * 70)

    user_id = "user123"
    print(f"User ID: {user_id}")

    # Generate token
    token = generate_token(user_id, {"role": "admin"})
    print(f"Token generated: {token[:50]}...")

    # Verify token
    payload = verify_token(token)
    print(f"Token payload: {payload}")
    assert payload is not None, "Token verification failed!"
    assert payload["user_id"] == user_id, "User ID mismatch!"
    assert payload["role"] == "admin", "Role mismatch!"

    # Verify invalid token
    invalid_payload = verify_token("invalid.token.here")
    print(f"Invalid token verification: {invalid_payload}")
    assert invalid_payload is None, "Invalid token should not verify!"

    print("✅ JWT tokens: PASSED")


def test_encryption():
    """Test encryption and decryption."""
    print("\n" + "=" * 70)
    print("TEST 3: Encryption")
    print("=" * 70)

    original = "This is secret data that needs encryption!"
    print(f"Original: {original}")

    # Encrypt
    encrypted = encryptor.encrypt(original)
    print(f"Encrypted: {encrypted[:50]}...")
    assert encrypted != original, "Data not encrypted!"

    # Decrypt
    decrypted = encryptor.decrypt(encrypted)
    print(f"Decrypted: {decrypted}")
    assert decrypted == original, "Decryption failed!"

    print("✅ Encryption: PASSED")


def test_input_sanitization():
    """Test input sanitization."""
    print("\n" + "=" * 70)
    print("TEST 4: Input Sanitization")
    print("=" * 70)

    dangerous_input = "<script>alert('XSS')</script>"
    print(f"Dangerous input: {dangerous_input}")

    sanitized = sanitize_input(dangerous_input)
    print(f"Sanitized: {sanitized}")
    assert "<script>" not in sanitized, "Script tags not sanitized!"
    assert "&lt;script&gt;" in sanitized, "Not properly escaped!"

    print("✅ Input sanitization: PASSED")


def test_phone_validation():
    """Test phone number validation."""
    print("\n" + "=" * 70)
    print("TEST 5: Phone Validation")
    print("=" * 70)

    valid_phones = [
        "0700000000",
        "+254700000000",
        "254700000000",
        "0100000000",
    ]

    invalid_phones = [
        "123",
        "invalid",
        "070000",  # Too short
        "abcdefghij",
    ]

    print("Valid phones:")
    for phone in valid_phones:
        result = validate_phone(phone)
        print(f"  {phone}: {result}")
        assert result, f"{phone} should be valid!"

    print("\nInvalid phones:")
    for phone in invalid_phones:
        result = validate_phone(phone)
        print(f"  {phone}: {result}")
        assert not result, f"{phone} should be invalid!"

    print("✅ Phone validation: PASSED")


def test_email_validation():
    """Test email validation."""
    print("\n" + "=" * 70)
    print("TEST 6: Email Validation")
    print("=" * 70)

    valid_emails = [
        "user@example.com",
        "test.user@domain.co.ke",
        "admin+tag@company.org",
    ]

    invalid_emails = [
        "invalid",
        "@example.com",
        "user@",
        "user @example.com",
    ]

    print("Valid emails:")
    for email in valid_emails:
        result = validate_email(email)
        print(f"  {email}: {result}")
        assert result, f"{email} should be valid!"

    print("\nInvalid emails:")
    for email in invalid_emails:
        result = validate_email(email)
        print(f"  {email}: {result}")
        assert not result, f"{email} should be invalid!"

    print("✅ Email validation: PASSED")


def test_api_keys():
    """Test API key generation and verification."""
    print("\n" + "=" * 70)
    print("TEST 7: API Keys")
    print("=" * 70)

    # Generate API key
    api_key = generate_api_key()
    print(f"Generated API key: {api_key[:20]}...")

    # Hash API key
    key_hash = hash_api_key(api_key)
    print(f"Hashed API key: {key_hash[:40]}...")

    # Verify correct key
    is_valid = verify_api_key(api_key, key_hash)
    print(f"Correct key verification: {is_valid}")
    assert is_valid, "API key verification failed!"

    # Verify wrong key
    is_invalid = verify_api_key("wrong_key_here", key_hash)
    print(f"Wrong key verification: {is_invalid}")
    assert not is_invalid, "Wrong key should not verify!"

    print("✅ API keys: PASSED")


def test_environment_variables():
    """Test environment variable loading."""
    print("\n" + "=" * 70)
    print("TEST 8: Environment Variables")
    print("=" * 70)

    env_vars = [
        "APP_NAME",
        "SECRET_KEY",
        "JWT_SECRET_KEY",
        "DATABASE_URL",
        "ENVIRONMENT",
    ]

    for var in env_vars:
        value = os.getenv(var)
        status = "✅ SET" if value else "❌ NOT SET"
        display_value = f"{value[:20]}..." if value and len(value) > 20 else value
        print(f"  {var}: {status} ({display_value})")

    print("✅ Environment variables: CHECKED")


def main():
    """Run all security tests."""
    print("\n" + "=" * 70)
    print("AUTOM8 SECURITY TESTING SUITE")
    print("=" * 70)

    try:
        test_environment_variables()
        test_password_hashing()
        test_jwt_tokens()
        test_encryption()
        test_input_sanitization()
        test_phone_validation()
        test_email_validation()
        test_api_keys()

        print("\n" + "=" * 70)
        print("✅ ALL SECURITY TESTS PASSED!")
        print("=" * 70 + "\n")

        return 0
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
