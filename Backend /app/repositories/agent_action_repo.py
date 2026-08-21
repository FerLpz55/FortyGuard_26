from typing import Sequence
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.agent_action import AgentAction
from app.repositories.base import BaseRepository


class AgentActionRepository(BaseRepository[AgentAction, dict, dict]):
    def __init__(self, db: AsyncSession):
        super().__init__(AgentAction, db)

    async def log_action(
        self,
        site_id: UUID | None,
        action_type: str,
        trigger: str,
        input_data: dict,
        output_data: dict,
        status: str = "success",
        error_message: str | None = None,
        execution_time_ms: int | None = None,
    ) -> AgentAction:
        action = AgentAction(
            site_id=site_id,
            action_type=action_type,
            trigger=trigger,
            input_data=input_data,
            output_data=output_data,
            status=status,
            error_message=error_message,
            execution_time_ms=execution_time_ms,
        )
        self.db.add(action)
        await self.db.commit()
        await self.db.refresh(action)
        return action

    async def get_by_site(self, site_id: UUID, skip: int = 0, limit: int = 50) -> Sequence[AgentAction]:
        result = await self.db.execute(
            select(AgentAction)
            .where(AgentAction.site_id == site_id)
            .order_by(desc(AgentAction.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_recent_global(self, limit: int = 100) -> Sequence[AgentAction]:
        result = await self.db.execute(
            select(AgentAction).order_by(desc(AgentAction.created_at)).limit(limit)
        )
        return result.scalars().all()