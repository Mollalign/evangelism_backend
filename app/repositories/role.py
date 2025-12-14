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
    
    async def get_by_name(self, name: str) -> Optional[Role]:
        """
        Get role by name.
        
        Args:
            name: Role name
            
        Returns:
            Role instance or None if not found
        """
        stmt = select(Role).where(Role.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def ensure_default_roles(self):
        """
        Ensure default roles exist in the database.
        Seed: owner, admin, member, missionary, evangelist
        """
        default_roles = ["owner", "admin", "member", "missionary", "evangelist"]
        for role_name in default_roles:
            role = await self.get_by_name(role_name)
            if not role:
                await self.create(
                    name=role_name,
                    description=f"Global {role_name} role"
                )
# Removed account specific methods
