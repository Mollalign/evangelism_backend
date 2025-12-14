"""
Mission Service

Business logic for mission operations.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.mission import MissionRepository
from app.repositories.account import AccountRepository
from app.repositories.user import UserRepository
from app.repositories.mission_user import MissionUserRepository
from app.repositories.account_user import AccountUserRepository
from app.repositories.role import RoleRepository
from app.models.mission import Mission
from app.models.user import User
from app.models.mission_user import MissionRole
from app.schemas.mission import MissionCreate, MissionUpdate
from app.utils.email import send_invitation_email

class MissionService:
    """Service for mission operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.mission_repo = MissionRepository(db)
        self.account_repo = AccountRepository(db)
        self.user_repo = UserRepository(db)
        self.mission_user_repo = MissionUserRepository(db)
        self.account_user_repo = AccountUserRepository(db)
        self.role_repo = RoleRepository(db)
    
    async def create_mission(
        self,
        mission_data: MissionCreate,
        current_user: User
    ) -> Mission:
        """Create a new mission and handle assignments."""
        # Verify account exists and user has access
        account = await self.account_repo.get_by_id(mission_data.account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
    async def create_mission(
        self,
        mission_data: MissionCreate,
        current_user: User
    ) -> Mission:
        """Create a new mission and handle assignments."""
        # Verify account exists
        account = await self.account_repo.get_by_id(mission_data.account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        # Verify user has admin role in the account
        # Requirement: "Only admin can create mission"
        account_user = await self.account_user_repo.get_by_user_and_account(
            current_user.id, 
            account.id
        )
        
        if not account_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this account"
            )
            
        role = await self.role_repo.get_by_id(account_user.role_id)
        # Check for admin OR owner
        if not role or role.name not in ["admin", "owner"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only account admins/owners can create missions"
            )
             
        # Create mission
        mission = await self.mission_repo.create(
            account_id=UUID(mission_data.account_id),
            name=mission_data.name,
            start_date=mission_data.start_date,
            end_date=mission_data.end_date,
            location=mission_data.location,
            budget=mission_data.budget,
            created_by=current_user.id
        )
        
        # Process assignments
        if mission_data.assignments:
            for assignment in mission_data.assignments:
                user = await self.user_repo.get_by_email(assignment.email)
                if user:
                    # Assign directly
                    try:
                        role_enum = MissionRole(assignment.role.lower())
                    except ValueError:
                        # Fallback or skip
                        continue

                    await self.mission_user_repo.create(
                        mission_id=mission.id,
                        user_id=user.id,
                        role=role_enum
                    )
                else:
                    # Send Email Invitation
                    send_invitation_email(
                        email=assignment.email,
                        mission_name=mission.name,
                        role=assignment.role
                    )

        await self.db.commit()
        await self.db.refresh(mission)
        return mission
    async def get_mission(self, mission_id: str) -> Mission:
        """Get mission by ID."""
        mission = await self.mission_repo.get_by_id(mission_id)
        if not mission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mission not found"
            )
        return mission
    
    async def get_missions_by_account(
        self,
        account_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Mission]:
        """Get missions for an account."""
        return await self.mission_repo.get_by_account(account_id, skip, limit)
    
    async def update_mission(
        self,
        mission_id: str,
        mission_data: MissionUpdate,
        current_user: User
    ) -> Mission:
        """Update a mission."""
        mission = await self.get_mission(mission_id)
        
        # Verify user created the mission or has account access
        if mission.created_by != current_user.id:
            # TODO: Add account access check
            pass
        
        # Update mission
        update_data = mission_data.model_dump(exclude_unset=True)
        if "deleted_at" in update_data and update_data["deleted_at"]:
            from datetime import datetime
            update_data["deleted_at"] = datetime.fromisoformat(update_data["deleted_at"].replace("Z", "+00:00"))
        
        updated_mission = await self.mission_repo.update(mission_id, **update_data)
        await self.db.commit()
        await self.db.refresh(updated_mission)
        return updated_mission
    
    async def delete_mission(
        self,
        mission_id: str,
        current_user: User
    ) -> bool:
        """Soft delete a mission."""
        mission = await self.get_mission(mission_id)
        
        # Verify user created the mission
        if mission.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this mission"
            )
        
        from datetime import datetime, timezone
        await self.mission_repo.update(mission_id, deleted_at=datetime.now(timezone.utc))
        await self.db.commit()
        return True

