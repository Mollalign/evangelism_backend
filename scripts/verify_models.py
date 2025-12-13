import asyncio
import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import engine, Base, AsyncSessionLocal
from app.models import Account, User, Role, AccountUser, Mission, MissionUser, OutreachData, OutreachNumbers, Expense
from app.models.mission_user import MissionRole
from sqlalchemy import select

async def verify_models():
    print("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created.")

    async with AsyncSessionLocal() as session:
        print("Creating sample data...")
        
        # Create User
        user = User(
            full_name="Test User",
            email="test@example.com",
            password_hash="hashed_password"
        )
        session.add(user)
        await session.flush() # Flush to get ID
        print(f"Created User: {user}")

        # Create Account
        account = Account(
            account_name="Test Church",
            created_by=user.id
        )
        session.add(account)
        await session.flush()
        print(f"Created Account: {account}")

        # Create Role
        role = Role(
            name="Admin",
            description="Administrator"
        )
        session.add(role)
        await session.flush()
        print(f"Created Role: {role}")

        # Assign User to Account
        account_user = AccountUser(
            account_id=account.id,
            user_id=user.id,
            role_id=role.id
        )
        session.add(account_user)
        await session.flush()
        print(f"Created AccountUser: {account_user}")

        # Create Mission
        mission = Mission(
            account_id=account.id,
            name="Test Mission",
            created_by=user.id
        )
        session.add(mission)
        await session.flush()
        print(f"Created Mission: {mission}")

        # Assign User to Mission
        mission_user = MissionUser(
            mission_id=mission.id,
            user_id=user.id,
            role=MissionRole.LEADER
        )
        session.add(mission_user)
        await session.flush()
        print(f"Created MissionUser: {mission_user}")

        # Create Outreach Data
        outreach_data = OutreachData(
            account_id=account.id,
            mission_id=mission.id,
            full_name="Seeker",
            created_by_user_id=user.id
        )
        session.add(outreach_data)
        await session.flush()
        print(f"Created OutreachData: {outreach_data}")

        # Create Outreach Numbers
        outreach_numbers = OutreachNumbers(
            account_id=account.id,
            mission_id=mission.id,
            saved=5
        )
        session.add(outreach_numbers)
        await session.flush()
        print(f"Created OutreachNumbers: {outreach_numbers}")

        # Create Expense
        expense = Expense(
            account_id=account.id,
            mission_id=mission.id,
            user_id=user.id,
            category="Travel",
            amount=100.0
        )
        session.add(expense)
        await session.flush()
        print(f"Created Expense: {expense}")

        await session.commit()
        print("Data committed.")

        # Verify Relationships
        print("Verifying relationships...")
        
        # Check Account -> Users
        stmt = select(Account).where(Account.id == account.id)
        result = await session.execute(stmt)
        fetched_account = result.scalar_one()
        # Accessing relationship triggers lazy load, which might fail in async if not careful with loading strategies or awaitable attributes
        # But here we are in the same session, so it might work if we use selectinload or similar options in query, 
        # OR we just query the association table directly to verify.
        # For simplicity in this script, let's just query the association table.
        
        stmt = select(AccountUser).where(AccountUser.account_id == account.id)
        result = await session.execute(stmt)
        fetched_account_users = result.scalars().all()
        print(f"Account Users count: {len(fetched_account_users)}")
        assert len(fetched_account_users) == 1

        # Check Mission -> OutreachData
        stmt = select(OutreachData).where(OutreachData.mission_id == mission.id)
        result = await session.execute(stmt)
        fetched_outreach = result.scalars().all()
        print(f"Mission Outreach Data count: {len(fetched_outreach)}")
        assert len(fetched_outreach) == 1

    print("Verification complete!")

if __name__ == "__main__":
    asyncio.run(verify_models())
