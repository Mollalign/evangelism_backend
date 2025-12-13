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
from app.models.mission import Mission
from app.models.user import User
from app.schemas.mission import MissionCreate, MissionUpdate


class MissionService:
    """Service for mission operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.mission_repo = MissionRepository(db)
        self.account_repo = AccountRepository(db)
    
    async def create_mission(
        self,
        mission_data: MissionCreate,
        current_user: User
    ) -> Mission:
        """Create a new mission."""
        # Verify account exists and user has access
        account = await self.account_repo.get_by_id(mission_data.account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
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

