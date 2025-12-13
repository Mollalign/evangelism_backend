#!/usr/bin/env python3
"""
Test script for authentication endpoints.

This script tests the authentication API endpoints.
Make sure the server is running before executing this script.

Usage:
    python scripts/test_auth_endpoints.py
"""

import asyncio
import sys
import os
import httpx
from datetime import datetime

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1/auth"


async def test_register():
    """Test user registration."""
    print("=" * 60)
    print("Testing User Registration")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        # Test registration
        register_data = {
            "full_name": "Test User",
            "email": f"test_{datetime.now().timestamp()}@example.com",
            "password": "testpass123",
            "phone_number": "+1234567890"
        }
        
        try:
            response = await client.post(f"{API_BASE}/register", json=register_data)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 201:
                data = response.json()
                print("✅ Registration successful!")
                print(f"   User ID: {data['user']['id']}")
                print(f"   Email: {data['user']['email']}")
                print(f"   Access Token: {data['access_token'][:50]}...")
                return data
            else:
                print(f"❌ Registration failed: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None


async def test_login(email: str, password: str):
    """Test user login."""
    print("\n" + "=" * 60)
    print("Testing User Login")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        login_data = {
            "email": email,
            "password": password
        }
        
        try:
            response = await client.post(f"{API_BASE}/login", json=login_data)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Login successful!")
                print(f"   User: {data['user']['full_name']}")
                print(f"   Access Token: {data['access_token'][:50]}...")
                return data
            else:
                print(f"❌ Login failed: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None


async def test_get_me(access_token: str):
    """Test getting current user."""
    print("\n" + "=" * 60)
    print("Testing Get Current User")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = await client.get(f"{API_BASE}/me", headers=headers)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Get current user successful!")
                print(f"   User: {data['full_name']}")
                print(f"   Email: {data['email']}")
                print(f"   Active: {data['is_active']}")
                return data
            else:
                print(f"❌ Get current user failed: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None


async def test_refresh_token(refresh_token: str):
    """Test token refresh."""
    print("\n" + "=" * 60)
    print("Testing Token Refresh")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        refresh_data = {
            "refresh_token": refresh_token
        }
        
        try:
            response = await client.post(f"{API_BASE}/refresh", json=refresh_data)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Token refresh successful!")
                print(f"   New Access Token: {data['access_token'][:50]}...")
                return data
            else:
                print(f"❌ Token refresh failed: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None


async def test_logout(access_token: str):
    """Test logout."""
    print("\n" + "=" * 60)
    print("Testing Logout")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = await client.post(f"{API_BASE}/logout", headers=headers)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Logout successful!")
                print(f"   Message: {data['message']}")
                return True
            else:
                print(f"❌ Logout failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


async def test_invalid_credentials():
    """Test login with invalid credentials."""
    print("\n" + "=" * 60)
    print("Testing Invalid Credentials")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        try:
            response = await client.post(f"{API_BASE}/login", json=login_data)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 401:
                print("✅ Invalid credentials correctly rejected!")
                return True
            else:
                print(f"❌ Expected 401, got {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


async def main():
    """Run all authentication tests."""
    print("\n" + "=" * 60)
    print("Authentication Endpoints Test Suite")
    print("=" * 60)
    print("\n⚠️  Make sure the server is running on http://localhost:8000")
    print("   Start with: uvicorn app.main:app --reload\n")
    
    try:
        # Test registration
        register_result = await test_register()
        if not register_result:
            print("\n❌ Registration failed, cannot continue tests")
            return
        
        user_email = register_result["user"]["email"]
        user_password = "testpass123"
        access_token = register_result["access_token"]
        refresh_token = register_result["refresh_token"]
        
        # Test login
        login_result = await test_login(user_email, user_password)
        if login_result:
            access_token = login_result["access_token"]  # Update with new token
        
        # Test get current user
        await test_get_me(access_token)
        
        # Test token refresh
        refresh_result = await test_refresh_token(refresh_token)
        if refresh_result:
            access_token = refresh_result["access_token"]
        
        # Test logout
        await test_logout(access_token)
        
        # Test invalid credentials
        await test_invalid_credentials()
        
        print("\n" + "=" * 60)
        print("✅ All authentication tests completed!")
        print("=" * 60)
        
    except httpx.ConnectError:
        print("\n❌ Could not connect to server!")
        print("   Make sure the server is running: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

