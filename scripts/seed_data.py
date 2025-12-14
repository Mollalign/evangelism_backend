"""
Database Seeding Script

This script seeds the database with default data for development and testing.
Run with: python scripts/seed_data.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import ssl
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User
from app.models.account import Account
from app.models.role import Role
from app.models.account_user import AccountUser
from app.models.mission import Mission
from app.models.outreach import OutreachData, OutreachNumbers
from app.models.expense import Expense
from datetime import datetime, timedelta


async def seed_database():
    """Seed the database with default data."""
    
    # Create database engine
    # Convert AnyUrl to string and ensure async driver
    db_url = str(settings.DATABASE_URL)
    
    # Remove query parameters (sslmode, etc.) as asyncpg handles SSL differently
    if "?" in db_url:
        db_url = db_url.split("?")[0]
    
    # Ensure async driver
    if db_url.startswith("postgresql://") or db_url.startswith("postgresql+psycopg2://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        db_url = db_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    
    # Build SSL context for cloud PostgreSQL (Neon) - same as database.py
    def build_ssl_context():
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        return ssl_context
    
    ssl_context = build_ssl_context()
    
    engine = create_async_engine(
        db_url,
        echo=False,
        connect_args={
            "ssl": ssl_context,
            "server_settings": {
                "application_name": "seed_script",
            }
        },
    )
    
    # Create session factory
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            print("🌱 Starting database seeding...")
            
            # 1. Create Default Users
            print("\n📝 Creating default users...")
            
            # Admin User
            admin_user = await session.execute(
                select(User).where(User.email == "admin@cmoms.com")
            )
            admin_user_obj = admin_user.scalar_one_or_none()
            
            if not admin_user_obj:
                admin_user_obj = User(
                    email="admin@cmoms.com",
                    password_hash=hash_password("admin123"),
                    full_name="Admin User",
                    phone_number="+1234567890",
                    is_active=True
                )
                session.add(admin_user_obj)
                await session.flush()
                print("  ✅ Created admin user: admin@cmoms.com / admin123")
            else:
                print("  ℹ️  Admin user already exists")
            
            # Missionary User
            missionary_user = await session.execute(
                select(User).where(User.email == "missionary@cmoms.com")
            )
            missionary_user_obj = missionary_user.scalar_one_or_none()
            
            if not missionary_user_obj:
                missionary_user_obj = User(
                    email="missionary@cmoms.com",
                    password_hash=hash_password("missionary123"),
                    full_name="John Missionary",
                    phone_number="+1234567891",
                    is_active=True
                )
                session.add(missionary_user_obj)
                await session.flush()
                print("  ✅ Created missionary user: missionary@cmoms.com / missionary123")
            else:
                print("  ℹ️  Missionary user already exists")
            
            # Test User
            test_user = await session.execute(
                select(User).where(User.email == "test@cmoms.com")
            )
            test_user_obj = test_user.scalar_one_or_none()
            
            if not test_user_obj:
                test_user_obj = User(
                    email="test@cmoms.com",
                    password_hash=hash_password("test123"),
                    full_name="Test User",
                    phone_number="+1234567892",
                    is_active=True
                )
                session.add(test_user_obj)
                await session.flush()
                print("  ✅ Created test user: test@cmoms.com / test123")
            else:
                print("  ℹ️  Test user already exists")
            
            await session.commit()
            await session.refresh(admin_user_obj)
            await session.refresh(missionary_user_obj)
            await session.refresh(test_user_obj)
            
            # 2. Create Default Account
            print("\n🏢 Creating default account...")
            
            account = await session.execute(
                select(Account).where(Account.account_name == "CMOMS Main Account")
            )
            account_obj = account.scalar_one_or_none()
            
            if not account_obj:
                account_obj = Account(
                    account_name="CMOMS Main Account",
                    email="info@cmoms.com",
                    phone_number="+1234567800",
                    location="Addis Ababa, Ethiopia",
                    created_by=admin_user_obj.id,
                    is_active=True
                )
                session.add(account_obj)
                await session.flush()
                print("  ✅ Created default account: CMOMS Main Account")
            else:
                print("  ℹ️  Default account already exists")
            
            await session.commit()
            await session.refresh(account_obj)
            
            # 3. Create Default Roles
            print("\n👥 Creating default roles...")
            
            admin_role = await session.execute(
                select(Role).where(Role.name == "admin", Role.account_id == account_obj.id)
            )
            admin_role_obj = admin_role.scalar_one_or_none()
            
            if not admin_role_obj:
                admin_role_obj = Role(
                    account_id=account_obj.id,
                    name="admin",
                    description="Administrator role with full access",
                    created_by=admin_user_obj.id
                )
                session.add(admin_role_obj)
                await session.flush()
                print("  ✅ Created admin role")
            else:
                print("  ℹ️  Admin role already exists")
            
            missionary_role = await session.execute(
                select(Role).where(Role.name == "missionary", Role.account_id == account_obj.id)
            )
            missionary_role_obj = missionary_role.scalar_one_or_none()
            
            if not missionary_role_obj:
                missionary_role_obj = Role(
                    account_id=account_obj.id,
                    name="missionary",
                    description="Missionary role for field workers",
                    created_by=admin_user_obj.id
                )
                session.add(missionary_role_obj)
                await session.flush()
                print("  ✅ Created missionary role")
            else:
                print("  ℹ️  Missionary role already exists")
            
            await session.commit()
            await session.refresh(admin_role_obj)
            await session.refresh(missionary_role_obj)
            
            # 4. Link Users to Account with Roles
            print("\n🔗 Linking users to account...")
            
            # Admin -> Account (admin role)
            admin_account_user = await session.execute(
                select(AccountUser).where(
                    AccountUser.account_id == account_obj.id,
                    AccountUser.user_id == admin_user_obj.id
                )
            )
            if not admin_account_user.scalar_one_or_none():
                admin_account_user_obj = AccountUser(
                    account_id=account_obj.id,
                    user_id=admin_user_obj.id,
                    role_id=admin_role_obj.id,
                    created_by=admin_user_obj.id
                )
                session.add(admin_account_user_obj)
                print("  ✅ Linked admin user to account")
            
            # Missionary -> Account (missionary role)
            missionary_account_user = await session.execute(
                select(AccountUser).where(
                    AccountUser.account_id == account_obj.id,
                    AccountUser.user_id == missionary_user_obj.id
                )
            )
            if not missionary_account_user.scalar_one_or_none():
                missionary_account_user_obj = AccountUser(
                    account_id=account_obj.id,
                    user_id=missionary_user_obj.id,
                    role_id=missionary_role_obj.id,
                    created_by=admin_user_obj.id
                )
                session.add(missionary_account_user_obj)
                print("  ✅ Linked missionary user to account")
            
            await session.commit()
            
            # 5. Create Sample Missions
            print("\n🎯 Creating sample missions...")
            
            mission1_result = await session.execute(
                select(Mission).where(Mission.name == "Addis Ababa Outreach 2024")
            )
            mission1_obj = mission1_result.scalar_one_or_none()
            
            if not mission1_obj:
                mission1_obj = Mission(
                    account_id=account_obj.id,
                    name="Addis Ababa Outreach 2024",
                    start_date=datetime.now() - timedelta(days=30),
                    end_date=datetime.now() + timedelta(days=60),
                    location={
                        "name": "Addis Ababa",
                        "address": "Bole Sub-city, Addis Ababa, Ethiopia",
                        "latitude": 9.1450,
                        "longitude": 38.7667
                    },
                    budget=50000.0,
                    created_by=admin_user_obj.id
                )
                session.add(mission1_obj)
                await session.flush()
                print("  ✅ Created mission: Addis Ababa Outreach 2024")
            else:
                print("  ℹ️  Mission already exists")
            
            mission2_result = await session.execute(
                select(Mission).where(Mission.name == "Rural Evangelism Campaign")
            )
            mission2_obj = mission2_result.scalar_one_or_none()
            
            if not mission2_obj:
                mission2_obj = Mission(
                    account_id=account_obj.id,
                    name="Rural Evangelism Campaign",
                    start_date=datetime.now() - timedelta(days=10),
                    end_date=datetime.now() + timedelta(days=50),
                    location={
                        "name": "Hawassa",
                        "address": "Hawassa, Sidama Region, Ethiopia",
                        "latitude": 7.0621,
                        "longitude": 38.4764
                    },
                    budget=30000.0,
                    created_by=admin_user_obj.id
                )
                session.add(mission2_obj)
                await session.flush()
                print("  ✅ Created mission: Rural Evangelism Campaign")
            else:
                print("  ℹ️  Mission already exists")
            
            await session.commit()
            await session.refresh(mission1_obj)
            await session.refresh(mission2_obj)
            
            # 6. Create Sample Outreach Data
            print("\n📊 Creating sample outreach data...")
            
            outreach_count_result = await session.execute(
                select(OutreachData).where(OutreachData.mission_id == mission1_obj.id).limit(1)
            )
            if outreach_count_result.first() is None:
                outreach_data_list = [
                    OutreachData(
                        account_id=account_obj.id,
                        mission_id=mission1_obj.id,
                        full_name="Alemayehu Bekele",
                        phone_number="+251911234567",
                        status="saved",
                        created_by_user_id=missionary_user_obj.id
                    ),
                    OutreachData(
                        account_id=account_obj.id,
                        mission_id=mission1_obj.id,
                        full_name="Meron Tadesse",
                        phone_number="+251922345678",
                        status="interested",
                        created_by_user_id=missionary_user_obj.id
                    ),
                    OutreachData(
                        account_id=account_obj.id,
                        mission_id=mission1_obj.id,
                        full_name="Yonas Gebre",
                        phone_number="+251933456789",
                        status="saved",
                        created_by_user_id=missionary_user_obj.id
                    ),
                ]
                for outreach in outreach_data_list:
                    session.add(outreach)
                print("  ✅ Created 3 sample outreach contacts")
            else:
                print("  ℹ️  Outreach data already exists")
            
            await session.commit()
            
            # 7. Create Sample Outreach Numbers
            print("\n📈 Creating sample outreach numbers...")
            
            outreach_numbers = await session.execute(
                select(OutreachNumbers).where(OutreachNumbers.mission_id == mission1_obj.id)
            )
            if not outreach_numbers.scalar_one_or_none():
                numbers_obj = OutreachNumbers(
                    account_id=account_obj.id,
                    mission_id=mission1_obj.id,
                    interested=15,
                    heared=25,
                    saved=8
                )
                session.add(numbers_obj)
                print("  ✅ Created outreach numbers for mission")
            else:
                print("  ℹ️  Outreach numbers already exist")
            
            await session.commit()
            
            # 8. Create Sample Expenses
            print("\n💰 Creating sample expenses...")
            
            expense_count = await session.execute(
                select(Expense).where(Expense.mission_id == mission1_obj.id)
            )
            if expense_count.scalar_one_or_none() is None:
                expenses_list = [
                    Expense(
                        account_id=account_obj.id,
                        mission_id=mission1_obj.id,
                        user_id=missionary_user_obj.id,
                        category="Transportation",
                        amount=500.0,
                        description="Bus tickets for team"
                    ),
                    Expense(
                        account_id=account_obj.id,
                        mission_id=mission1_obj.id,
                        user_id=missionary_user_obj.id,
                        category="Materials",
                        amount=1200.0,
                        description="Bibles and literature"
                    ),
                    Expense(
                        account_id=account_obj.id,
                        mission_id=mission1_obj.id,
                        user_id=missionary_user_obj.id,
                        category="Food",
                        amount=800.0,
                        description="Team meals"
                    ),
                ]
                for expense in expenses_list:
                    session.add(expense)
                print("  ✅ Created 3 sample expenses")
            else:
                print("  ℹ️  Expenses already exist")
            
            await session.commit()
            
            print("\n✅ Database seeding completed successfully!")
            print("\n📋 Default Credentials:")
            print("  Admin:     admin@cmoms.com / admin123")
            print("  Missionary: missionary@cmoms.com / missionary123")
            print("  Test:     test@cmoms.com / test123")
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error seeding database: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())

