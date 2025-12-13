"""
Outreach Repository

Repository for outreach database operations.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.outreach import OutreachData, OutreachNumbers
from app.repositories.base import BaseRepository


class OutreachDataRepository(BaseRepository[OutreachData]):
    """Repository for OutreachData model operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(OutreachData, db)
    
    async def get_by_mission(
        self,
        mission_id: UUID | str,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False
    ) -> List[OutreachData]:
        """Get outreach data for a mission."""
        if isinstance(mission_id, str):
            try:
                mission_id = UUID(mission_id)
            except ValueError:
                return []
        
        stmt = select(OutreachData).where(OutreachData.mission_id == mission_id)
        
        if not include_deleted:
            stmt = stmt.where(OutreachData.deleted_at.is_(None))
        
        stmt = stmt.offset(skip).limit(limit).order_by(OutreachData.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_account(
        self,
        account_id: UUID | str,
        skip: int = 0,
        limit: int = 100
    ) -> List[OutreachData]:
        """Get outreach data for an account."""
        if isinstance(account_id, str):
            try:
                account_id = UUID(account_id)
            except ValueError:
                return []
        
        stmt = (
            select(OutreachData)
            .where(and_(OutreachData.account_id == account_id, OutreachData.deleted_at.is_(None)))
            .offset(skip)
            .limit(limit)
            .order_by(OutreachData.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class OutreachNumbersRepository(BaseRepository[OutreachNumbers]):
    """Repository for OutreachNumbers model operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(OutreachNumbers, db)
    
    async def get_by_mission(
        self,
        mission_id: UUID | str
    ) -> Optional[OutreachNumbers]:
        """Get outreach numbers for a mission (one-to-one relationship)."""
        if isinstance(mission_id, str):
            try:
                mission_id = UUID(mission_id)
            except ValueError:
                return None
        
        stmt = select(OutreachNumbers).where(
            and_(
                OutreachNumbers.mission_id == mission_id,
                OutreachNumbers.deleted_at.is_(None)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_account(
        self,
        account_id: UUID | str,
        skip: int = 0,
        limit: int = 100
    ) -> List[OutreachNumbers]:
        """Get outreach numbers for an account."""
        if isinstance(account_id, str):
            try:
                account_id = UUID(account_id)
            except ValueError:
                return []
        
        stmt = (
            select(OutreachNumbers)
            .where(and_(OutreachNumbers.account_id == account_id, OutreachNumbers.deleted_at.is_(None)))
            .offset(skip)
            .limit(limit)
            .order_by(OutreachNumbers.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

