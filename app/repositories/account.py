"""
Account Repository

Repository for account database operations.
"""

from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.account import Account
from app.repositories.base import BaseRepository


class AccountRepository(BaseRepository[Account]):
    """Repository for Account model operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Account, db)

