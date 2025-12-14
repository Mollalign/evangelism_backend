"""
AccountUser Repository

Repository for account_user database operations.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.account_user import AccountUser
from app.repositories.base import BaseRepository


class AccountUserRepository(BaseRepository[AccountUser]):
    """Repository for AccountUser model operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(AccountUser, db)
    
    async def get_by_user_id(self, user_id: UUID | str) -> List[AccountUser]:
        """
        Get all account-user relationships for a user.
        
        Args:
            user_id: User UUID (as UUID or string)
            
        Returns:
            List of AccountUser instances
        """
        if isinstance(user_id, str):
            try:
                user_id = UUID(user_id)
            except ValueError:
                return []
        
        stmt = select(AccountUser).where(
            AccountUser.user_id == user_id,
            AccountUser.deleted_at.is_(None)  # Only active relationships
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_account_id(self, account_id: UUID | str) -> List[AccountUser]:
        """
        Get all account-user relationships for an account.
        
        Args:
            account_id: Account UUID (as UUID or string)
            
        Returns:
            List of AccountUser instances
        """
        if isinstance(account_id, str):
            try:
                account_id = UUID(account_id)
            except ValueError:
                return []
        
        stmt = select(AccountUser).where(
            AccountUser.account_id == account_id,
            AccountUser.deleted_at.is_(None)  # Only active relationships
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_user_and_account(
        self,
        user_id: UUID | str,
        account_id: UUID | str
    ) -> Optional[AccountUser]:
        """
        Get account-user relationship for specific user and account.
        
        Args:
            user_id: User UUID (as UUID or string)
            account_id: Account UUID (as UUID or string)
            
        Returns:
            AccountUser instance or None if not found
        """
        if isinstance(user_id, str):
            try:
                user_id = UUID(user_id)
            except ValueError:
                return None
        
        if isinstance(account_id, str):
            try:
                account_id = UUID(account_id)
            except ValueError:
                return None
        
        stmt = select(AccountUser).where(
            AccountUser.user_id == user_id,
            AccountUser.account_id == account_id,
            AccountUser.deleted_at.is_(None)  # Only active relationships
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create(
        self,
        account_id: UUID | str,
        user_id: UUID | str,
        role_id: UUID | str
    ) -> AccountUser:
        """
        Create a new account-user relationship.
        
        Args:
            account_id: Account UUID (as UUID or string)
            user_id: User UUID (as UUID or string)
            role_id: Role UUID (as UUID or string)
            
        Returns:
            Created AccountUser instance
        """
        if isinstance(account_id, str):
            account_id = UUID(account_id)
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        if isinstance(role_id, str):
            role_id = UUID(role_id)
        
        account_user = AccountUser(
            account_id=account_id,
            user_id=user_id,
            role_id=role_id
        )
        self.db.add(account_user)
        await self.db.flush()
        await self.db.refresh(account_user)
        return account_user
