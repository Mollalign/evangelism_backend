"""
Outreach Service

Business logic for outreach operations.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.outreach import OutreachDataRepository, OutreachNumbersRepository
from app.repositories.mission import MissionRepository
from app.repositories.account import AccountRepository
from app.models.outreach import OutreachData, OutreachNumbers
from app.models.user import User
from app.schemas.outreach import (
    OutreachDataCreate,
    OutreachDataUpdate,
    OutreachNumbersCreate,
    OutreachNumbersUpdate
)


class OutreachService:
    """Service for outreach operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.outreach_data_repo = OutreachDataRepository(db)
        self.outreach_numbers_repo = OutreachNumbersRepository(db)
        self.mission_repo = MissionRepository(db)
        self.account_repo = AccountRepository(db)
    
    # Outreach Data methods
    async def create_outreach_data(
        self,
        outreach_data: OutreachDataCreate,
        current_user: User
    ) -> OutreachData:
        """Create new outreach data."""
        # Verify mission exists
        mission = await self.mission_repo.get_by_id(outreach_data.mission_id)
        if not mission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mission not found"
            )
        
        # Create outreach data
        data = await self.outreach_data_repo.create(
            account_id=UUID(outreach_data.account_id),
            mission_id=UUID(outreach_data.mission_id),
            full_name=outreach_data.full_name,
            phone_number=outreach_data.phone_number,
            status=outreach_data.status,
            created_by_user_id=current_user.id
        )
        
        await self.db.commit()
        await self.db.refresh(data)
        return data
    
    async def get_outreach_data(self, data_id: str) -> OutreachData:
        """Get outreach data by ID."""
        data = await self.outreach_data_repo.get_by_id(data_id)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Outreach data not found"
            )
        return data
    
    async def get_outreach_data_by_mission(
        self,
        mission_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[OutreachData]:
        """Get outreach data for a mission."""
        return await self.outreach_data_repo.get_by_mission(mission_id, skip, limit)
    
    async def update_outreach_data(
        self,
        data_id: str,
        update_data: OutreachDataUpdate,
        current_user: User
    ) -> OutreachData:
        """Update outreach data."""
        data = await self.get_outreach_data(data_id)
        
        # Verify user created the data
        if data.created_by_user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this outreach data"
            )
        
        update_dict = update_data.model_dump(exclude_unset=True)
        if "deleted_at" in update_dict and update_dict["deleted_at"]:
            from datetime import datetime
            update_dict["deleted_at"] = datetime.fromisoformat(update_dict["deleted_at"].replace("Z", "+00:00"))
        
        updated = await self.outreach_data_repo.update(data_id, **update_dict)
        await self.db.commit()
        await self.db.refresh(updated)
        return updated
    
    # Outreach Numbers methods
    async def get_or_create_outreach_numbers(
        self,
        numbers_data: OutreachNumbersCreate
    ) -> OutreachNumbers:
        """Get or create outreach numbers for a mission."""
        # Check if exists
        existing = await self.outreach_numbers_repo.get_by_mission(numbers_data.mission_id)
        
        if existing:
            # Update existing
            update_data = OutreachNumbersUpdate(
                interested=numbers_data.interested,
                heared=numbers_data.heared,
                saved=numbers_data.saved
            )
            update_dict = update_data.model_dump(exclude_unset=True)
            updated = await self.outreach_numbers_repo.update(str(existing.id), **update_dict)
            await self.db.commit()
            await self.db.refresh(updated)
            return updated
        else:
            # Create new
            numbers = await self.outreach_numbers_repo.create(
                account_id=UUID(numbers_data.account_id),
                mission_id=UUID(numbers_data.mission_id),
                interested=numbers_data.interested,
                heared=numbers_data.heared,
                saved=numbers_data.saved
            )
            await self.db.commit()
            await self.db.refresh(numbers)
            return numbers
    
    async def get_outreach_numbers(self, mission_id: str) -> Optional[OutreachNumbers]:
        """Get outreach numbers for a mission."""
        return await self.outreach_numbers_repo.get_by_mission(mission_id)

