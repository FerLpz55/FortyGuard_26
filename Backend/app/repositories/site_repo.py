from typing import Optional, Sequence
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.site import Site
from app.models.user import User
from app.repositories.base import BaseRepository

class SiteRepository(BaseRepository[Site]):
    """Repository for Site model operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Site, db)

    async def get_by_user(self, user_id: UUID, *, skip: int = 0, limit: int = 100) -> Sequence[Site]:
        """Retrieve sites belonging to a specific user with pagination."""
        stmt = select(Site).where(Site.user_id == user_id).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def count_by_user(self, user_id: UUID) -> int:
        """Count total sites for a specific user."""
        stmt = select(func.count()).select_from(Site).where(Site.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_all_active(self) -> Sequence[Site]:
        """Retrieve all sites whose owners are active users."""
        stmt = select(Site).join(User).where(User.is_active == True)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_id_and_user(self, site_id: UUID, user_id: UUID) -> Optional[Site]:
        """Retrieve a site by its ID, ensuring it belongs to the given user."""
        stmt = select(Site).where(Site.id == site_id, Site.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
