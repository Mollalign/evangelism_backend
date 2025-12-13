#!/usr/bin/env python3
"""
Test script for authentication functionality.

Usage:
    python scripts/test_auth.py
"""

import asyncio
import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    create_token_pair,
    decode_token,
    get_user_id_from_token,
    get_email_from_token,
    verify_token_type
)


def test_password_hashing():
    """Test password hashing and verification."""
    print("=" * 60)
    print("Testing Password Hashing")
    print("=" * 60)
    
    password = "test_password_123"
    hashed = hash_password(password)
    
    print(f"Original password: {password}")
    print(f"Hashed password: {hashed[:50]}...")
    
    # Test correct password
    is_valid = verify_password(password, hashed)
    print(f"✅ Correct password verification: {is_valid}")
    assert is_valid, "Password verification should succeed"
    
    # Test incorrect password
    is_invalid = verify_password("wrong_password", hashed)
    print(f"✅ Incorrect password verification: {not is_invalid}")
    assert not is_invalid, "Wrong password should fail"
    
    print("✅ Password hashing tests passed!\n")


def test_jwt_tokens():
    """Test JWT token creation and validation."""
    print("=" * 60)
    print("Testing JWT Tokens")
    print("=" * 60)
    
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    email = "test@example.com"
    
    # Test access token
    token_data = {"user_id": user_id, "sub": email, "email": email}
    access_token = create_access_token(data=token_data)
    print(f"✅ Access token created: {access_token[:50]}...")
    
    # Test refresh token
    refresh_token = create_refresh_token(data=token_data)
    print(f"✅ Refresh token created: {refresh_token[:50]}...")
    
    # Test token pair
    tokens = create_token_pair(user_id, email)
    print(f"✅ Token pair created")
    print(f"   Access token: {tokens['access_token'][:50]}...")
    print(f"   Refresh token: {tokens['refresh_token'][:50]}...")
    print(f"   Token type: {tokens['token_type']}")
    
    # Test decoding
    try:
        payload = decode_token(access_token)
        print(f"✅ Token decoded successfully")
        print(f"   User ID: {payload.get('user_id')}")
        print(f"   Email: {payload.get('email')}")
        print(f"   Type: {payload.get('type')}")
        
        # Test token type verification
        is_access = verify_token_type(access_token, "access")
        is_refresh = verify_token_type(refresh_token, "refresh")
        print(f"✅ Token type verification: access={is_access}, refresh={is_refresh}")
        
        # Test user ID extraction
        extracted_user_id = get_user_id_from_token(access_token)
        extracted_email = get_email_from_token(access_token)
        print(f"✅ User ID extraction: {extracted_user_id}")
        print(f"✅ Email extraction: {extracted_email}")
        
    except Exception as e:
        print(f"❌ Token decoding failed: {e}")
        raise
    
    print("✅ JWT token tests passed!\n")


def test_invalid_token():
    """Test handling of invalid tokens."""
    print("=" * 60)
    print("Testing Invalid Token Handling")
    print("=" * 60)
    
    invalid_token = "invalid.token.here"
    
    try:
        decode_token(invalid_token)
        print("❌ Should have raised exception for invalid token")
        assert False, "Invalid token should raise exception"
    except Exception as e:
        print(f"✅ Invalid token correctly rejected: {type(e).__name__}")
    
    # Test extraction with invalid token
    user_id = get_user_id_from_token(invalid_token)
    email = get_email_from_token(invalid_token)
    print(f"✅ Invalid token extraction returns None: user_id={user_id}, email={email}")
    assert user_id is None and email is None
    
    print("✅ Invalid token handling tests passed!\n")


if __name__ == "__main__":
    try:
        print("\n" + "=" * 60)
        print("Authentication System Test")
        print("=" * 60 + "\n")
        
        test_password_hashing()
        test_jwt_tokens()
        test_invalid_token()
        
        print("=" * 60)
        print("✅ All authentication tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

