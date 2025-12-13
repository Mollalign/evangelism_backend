"""
Mission Repository

Repository for mission database operations.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.mission import Mission
from app.repositories.base import BaseRepository


class MissionRepository(BaseRepository[Mission]):
    """Repository for Mission model operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Mission, db)
    
    async def get_by_account(
        self,
        account_id: UUID | str,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False
    ) -> List[Mission]:
        """
        Get missions for an account.
        
        Args:
            account_id: Account UUID
            skip: Number of records to skip
            limit: Maximum number of records
            include_deleted: Whether to include deleted missions
            
        Returns:
            List of Mission instances
        """
        if isinstance(account_id, str):
            try:
                account_id = UUID(account_id)
            except ValueError:
                return []
        
        stmt = select(Mission).where(Mission.account_id == account_id)
        
        if not include_deleted:
            stmt = stmt.where(Mission.deleted_at.is_(None))
        
        stmt = stmt.offset(skip).limit(limit).order_by(Mission.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_creator(
        self,
        user_id: UUID | str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Mission]:
        """Get missions created by a user."""
        if isinstance(user_id, str):
            try:
                user_id = UUID(user_id)
            except ValueError:
                return []
        
        stmt = (
            select(Mission)
            .where(and_(Mission.created_by == user_id, Mission.deleted_at.is_(None)))
            .offset(skip)
            .limit(limit)
            .order_by(Mission.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

