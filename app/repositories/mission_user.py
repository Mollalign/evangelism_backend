"""
Mission User Repository

Repository for mission user database operations.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.mission_user import MissionUser
from app.repositories.base import BaseRepository

class MissionUserRepository(BaseRepository[MissionUser]):
    """Repository for MissionUser model operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(MissionUser, db)
