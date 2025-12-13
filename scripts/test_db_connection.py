#!/usr/bin/env python3
"""
Simple script to test database connection.

Usage:
    python scripts/test_db_connection.py
"""

import asyncio
import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import check_db_connection, engine, DatabaseManager
from app.core.config import settings
from sqlalchemy import text, inspect


async def test_connection():
    """Test basic database connection."""
    print("=" * 60)
    print("Testing Database Connection")
    print("=" * 60)
    print(f"Database URL: {settings.DATABASE_URL}")
    print()
    
    # Test 1: Basic connection check
    print("Test 1: Basic Connection Check")
    print("-" * 60)
    try:
        is_healthy = await check_db_connection()
        if is_healthy:
            print("✅ Database connection successful!")
        else:
            print("❌ Database connection failed!")
            return False
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return False
    print()
    
    # Test 2: Get database version
    print("Test 2: Database Version")
    print("-" * 60)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ PostgreSQL Version: {version}")
    except Exception as e:
        print(f"❌ Error getting version: {e}")
        return False
    print()
    
    # Test 3: Check if tables exist
    print("Test 3: Checking Tables")
    print("-" * 60)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            if tables:
                print(f"✅ Found {len(tables)} table(s):")
                for table in tables:
                    print(f"   - {table}")
            else:
                print("⚠️  No tables found. You may need to run migrations:")
                print("   alembic upgrade head")
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return False
    print()
    
    # Test 4: Using DatabaseManager
    print("Test 4: DatabaseManager Health Check")
    print("-" * 60)
    try:
        is_healthy = await DatabaseManager.health_check()
        if is_healthy:
            print("✅ DatabaseManager health check passed!")
        else:
            print("❌ DatabaseManager health check failed!")
            return False
    except Exception as e:
        print(f"❌ Error in DatabaseManager health check: {e}")
        return False
    print()
    
    print("=" * 60)
    print("✅ All database tests passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_connection())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

