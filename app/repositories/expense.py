"""
Expense Repository

Repository for expense database operations.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.expense import Expense
from app.repositories.base import BaseRepository


class ExpenseRepository(BaseRepository[Expense]):
    """Repository for Expense model operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Expense, db)
    
    async def get_by_mission(
        self,
        mission_id: UUID | str,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False
    ) -> List[Expense]:
        """Get expenses for a mission."""
        if isinstance(mission_id, str):
            try:
                mission_id = UUID(mission_id)
            except ValueError:
                return []
        
        stmt = select(Expense).where(Expense.mission_id == mission_id)
        
        if not include_deleted:
            stmt = stmt.where(Expense.deleted_at.is_(None))
        
        stmt = stmt.offset(skip).limit(limit).order_by(Expense.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_account(
        self,
        account_id: UUID | str,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False
    ) -> List[Expense]:
        """Get expenses for an account."""
        if isinstance(account_id, str):
            try:
                account_id = UUID(account_id)
            except ValueError:
                return []
        
        stmt = select(Expense).where(Expense.account_id == account_id)
        
        if not include_deleted:
            stmt = stmt.where(Expense.deleted_at.is_(None))
        
        stmt = stmt.offset(skip).limit(limit).order_by(Expense.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_user(
        self,
        user_id: UUID | str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Expense]:
        """Get expenses created by a user."""
        if isinstance(user_id, str):
            try:
                user_id = UUID(user_id)
            except ValueError:
                return []
        
        stmt = (
            select(Expense)
            .where(and_(Expense.user_id == user_id, Expense.deleted_at.is_(None)))
            .offset(skip)
            .limit(limit)
            .order_by(Expense.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

