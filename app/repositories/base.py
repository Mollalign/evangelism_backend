"""
Base Repository

Abstract base class for repository pattern implementation.
"""

from typing import Generic, TypeVar, Optional, List, Type
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    Base repository class providing common CRUD operations.
    
    Usage:
        class UserRepository(BaseRepository[User]):
            def __init__(self, db: AsyncSession):
                super().__init__(User, db)
    """
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """
        Initialize repository.
        
        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db
    
    async def get_by_id(self, id: UUID | str) -> Optional[ModelType]:
        """
        Get a record by ID.
        
        Args:
            id: Record UUID (as UUID or string)
            
        Returns:
            Model instance or None if not found
        """
        if isinstance(id, str):
            try:
                id = UUID(id)
            except ValueError:
                return None
        
        stmt = select(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[ModelType]:
        """
        Get a record by email (if model has email field).
        
        Args:
            email: Email address
            
        Returns:
            Model instance or None if not found
        """
        if not hasattr(self.model, 'email'):
            raise AttributeError(f"{self.model.__name__} does not have an 'email' field")
        
        stmt = select(self.model).where(self.model.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None
    ) -> List[ModelType]:
        """
        Get all records with pagination and optional filters.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of field: value filters
            
        Returns:
            List of model instances
        """
        stmt = select(self.model)
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    stmt = stmt.where(getattr(self.model, field) == value)
        
        stmt = stmt.offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def create(self, **kwargs) -> ModelType:
        """
        Create a new record.
        
        Args:
            **kwargs: Model field values
            
        Returns:
            Created model instance
        """
        instance = self.model(**kwargs)
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance
    
    async def update(self, id: UUID | str, **kwargs) -> Optional[ModelType]:
        """
        Update a record by ID.
        
        Args:
            id: Record UUID (as UUID or string)
            **kwargs: Fields to update
            
        Returns:
            Updated model instance or None if not found
        """
        if isinstance(id, str):
            try:
                id = UUID(id)
            except ValueError:
                return None
        
        # Remove None values
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        
        if not kwargs:
            return await self.get_by_id(id)
        
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
        )
        await self.db.execute(stmt)
        await self.db.commit()
        
        return await self.get_by_id(id)
    
    async def delete(self, id: UUID | str) -> bool:
        """
        Delete a record by ID.
        
        Args:
            id: Record UUID (as UUID or string)
            
        Returns:
            True if deleted, False if not found
        """
        if isinstance(id, str):
            try:
                id = UUID(id)
            except ValueError:
                return False
        
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def count(self, filters: Optional[dict] = None) -> int:
        """
        Count records with optional filters.
        
        Args:
            filters: Dictionary of field: value filters
            
        Returns:
            Number of records
        """
        from sqlalchemy import func
        
        stmt = select(func.count()).select_from(self.model)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    stmt = stmt.where(getattr(self.model, field) == value)
        
        result = await self.db.execute(stmt)
        return result.scalar() or 0

