from typing import Sequence, Any
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_action import AgentAction
from app.repositories.base import BaseRepository

class AgentActionRepository(BaseRepository[AgentAction]):
    """Repository for AgentAction model operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(AgentAction, db)

    async def get_by_site(self, site_id: UUID, skip: int, limit: int) -> Sequence[AgentAction]:
        """Retrieve agent actions for a specific site, with pagination."""
        stmt = select(AgentAction).where(
            AgentAction.site_id == site_id
        ).order_by(AgentAction.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_recent(self, limit: int = 10) -> Sequence[AgentAction]:
        """Retrieve recent agent actions across all sites."""
        stmt = select(AgentAction).order_by(AgentAction.created_at.desc()).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_action(self, **kwargs: Any) -> AgentAction:
        """Convenience method to create an agent action."""
        return await self.create(**kwargs)
