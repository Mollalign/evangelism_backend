"""
User Repository

Repository for user database operations.
"""

from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: User's email address
            
        Returns:
            User instance or None if not found
        """
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def email_exists(self, email: str, exclude_id: Optional[UUID] = None) -> bool:
        """
        Check if email already exists.
        
        Args:
            email: Email address to check
            exclude_id: Optional user ID to exclude from check (for updates)
            
        Returns:
            True if email exists, False otherwise
        """
        stmt = select(User).where(User.email == email)
        
        if exclude_id:
            stmt = stmt.where(User.id != exclude_id)
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def create_user(
        self,
        email: str,
        password_hash: str,
        full_name: str,
        phone_number: Optional[str] = None,
        is_active: bool = True
    ) -> User:
        """
        Create a new user.
        
        Args:
            email: User's email address
            password_hash: Hashed password
            full_name: User's full name
            phone_number: Optional phone number
            is_active: Whether user is active
            
        Returns:
            Created User instance
        """
        user = User(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            phone_number=phone_number,
            is_active=is_active
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

