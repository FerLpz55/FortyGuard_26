from typing import TypeVar, Generic, Type, Optional, Sequence, Any
from uuid import UUID
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")

class BaseRepository(Generic[ModelType]):
    """Generic async repository with CRUD operations."""
    
    def __init__(self, model: Type[ModelType], db: AsyncSession) -> None:
        self.model = model
        self.db = db
    
    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Retrieve a record by its ID."""
        stmt = select(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
        
    async def get_all(self, *, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """Retrieve multiple records with pagination."""
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
        
    async def count(self) -> int:
        """Count total records."""
        stmt = select(func.count()).select_from(self.model)
        result = await self.db.execute(stmt)
        return result.scalar_one()
        
    async def create(self, **kwargs: Any) -> ModelType:
        """Create a new record."""
        obj = self.model(**kwargs)
        self.db.add(obj)
        await self.db.flush()
        return obj
        
    async def update(self, id: UUID, **kwargs: Any) -> Optional[ModelType]:
        """Update an existing record by ID."""
        obj = await self.get_by_id(id)
        if obj:
            for key, value in kwargs.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            await self.db.flush()
        return obj
        
    async def delete(self, id: UUID) -> bool:
        """Delete a record by ID."""
        obj = await self.get_by_id(id)
        if not obj:
            return False
        await self.db.delete(obj)
        await self.db.flush()
        return True
