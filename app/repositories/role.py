"""
Role Repository

Repository for role database operations.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.role import Role
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """Repository for Role model operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Role, db)
    
    async def get_by_account_id(self, account_id: UUID | str) -> List[Role]:
        """
        Get all roles for an account.
        
        Args:
            account_id: Account UUID (as UUID or string)
            
        Returns:
            List of Role instances
        """
        if isinstance(account_id, str):
            try:
                account_id = UUID(account_id)
            except ValueError:
                return []
        
        stmt = select(Role).where(Role.account_id == account_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_name_and_account(
        self,
        name: str,
        account_id: UUID | str
    ) -> Optional[Role]:
        """
        Get role by name and account.
        
        Args:
            name: Role name
            account_id: Account UUID (as UUID or string)
            
        Returns:
            Role instance or None if not found
        """
        if isinstance(account_id, str):
            try:
                account_id = UUID(account_id)
            except ValueError:
                return None
        
        stmt = select(Role).where(
            Role.name == name,
            Role.account_id == account_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
