from typing import Sequence
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.site import Site
from app.repositories.base import BaseRepository
from app.schemas.site import SiteCreate, SiteUpdate


class SiteRepository(BaseRepository[Site, SiteCreate, SiteUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Site, db)

    async def get_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> Sequence[Site]:
        result = await self.db.execute(
            select(Site).where(Site.user_id == user_id).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def count_by_user(self, user_id: UUID) -> int:
        result = await self.db.execute(select(func.count()).select_from(Site).where(Site.user_id == user_id))
        return result.scalar_one()

    async def get_active_by_user(self, user_id: UUID) -> Sequence[Site]:
        result = await self.db.execute(
            select(Site).where(Site.user_id == user_id, Site.metadata.op("->>")("is_active") != "false")
        )
        return result.scalars().all()

    async def get_all_active(self) -> Sequence[Site]:
        result = await self.db.execute(select(Site))
        return result.scalars().all()