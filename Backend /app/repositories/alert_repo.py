from typing import Sequence
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from app.models.alert import Alert
from app.repositories.base import BaseRepository
from app.schemas.alert import AlertCreate


class AlertRepository(BaseRepository[Alert, AlertCreate, dict]):
    def __init__(self, db: AsyncSession):
        super().__init__(Alert, db)

    async def get_by_site(
        self,
        site_id: UUID,
        skip: int = 0,
        limit: int = 20,
        severity: str | None = None,
        alert_type: str | None = None,
        acknowledged: bool | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> Sequence[Alert]:
        query = select(Alert).where(Alert.site_id == site_id)
        if severity:
            query = query.where(Alert.severity == severity)
        if alert_type:
            query = query.where(Alert.alert_type == alert_type)
        if acknowledged is not None:
            query = query.where(Alert.acknowledged == acknowledged)
        if start:
            query = query.where(Alert.created_at >= start)
        if end:
            query = query.where(Alert.created_at <= end)
        query = query.order_by(desc(Alert.created_at)).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_unacknowledged(self, site_id: UUID | None = None) -> Sequence[Alert]:
        query = select(Alert).where(Alert.acknowledged == False)
        if site_id:
            query = query.where(Alert.site_id == site_id)
        query = query.order_by(desc(Alert.created_at))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_summary(self, site_id: UUID | None = None) -> dict:
        query = select(Alert)
        if site_id:
            query = query.where(Alert.site_id == site_id)

        severity_counts = await self.db.execute(
            select(Alert.severity, func.count()).select_from(query.subquery()).group_by(Alert.severity)
        )
        type_counts = await self.db.execute(
            select(Alert.alert_type, func.count()).select_from(query.subquery()).group_by(Alert.alert_type)
        )
        unacked = await self.db.execute(
            select(func.count()).select_from(query.subquery()).where(Alert.acknowledged == False)
        )
        latest_critical = await self.db.execute(
            select(Alert).where(Alert.severity == "critical").order_by(desc(Alert.created_at)).limit(1)
        )

        return {
            "by_severity": {row.severity: row.count for row in severity_counts},
            "by_type": {row.alert_type: row.count for row in type_counts},
            "unacknowledged_count": unacked.scalar_one(),
            "latest_critical": latest_critical.scalar_one_or_none(),
        }

    async def acknowledge(self, alert_id: UUID, user_id: UUID) -> Alert | None:
        alert = await self.get(alert_id)
        if alert and not alert.acknowledged:
            alert.acknowledged = True
            alert.acknowledged_by = user_id
            alert.acknowledged_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(alert)
        return alert