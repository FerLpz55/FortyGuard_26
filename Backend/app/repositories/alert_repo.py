from typing import Optional, Sequence, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.models.site import Site
from app.repositories.base import BaseRepository

class AlertRepository(BaseRepository[Alert]):
    """Repository for Alert model operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Alert, db)

    async def get_by_site(
        self,
        site_id: UUID,
        *,
        severity: Optional[str] = None,
        alert_type: Optional[str] = None,
        acknowledged: Optional[bool] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[Sequence[Alert], int]:
        """Retrieve alerts for a site with optional filtering, paginated, and total count."""
        
        base_stmt = select(Alert).where(Alert.site_id == site_id)
        count_stmt = select(func.count()).select_from(Alert).where(Alert.site_id == site_id)

        conditions = []
        if severity is not None:
            conditions.append(Alert.severity == severity)
        if alert_type is not None:
            conditions.append(Alert.alert_type == alert_type)
        if acknowledged is not None:
            conditions.append(Alert.acknowledged == acknowledged)
        if start is not None:
            conditions.append(Alert.created_at >= start)
        if end is not None:
            conditions.append(Alert.created_at <= end)

        for condition in conditions:
            base_stmt = base_stmt.where(condition)
            count_stmt = count_stmt.where(condition)

        base_stmt = base_stmt.order_by(Alert.created_at.desc()).offset(skip).limit(limit)

        items_result = await self.db.execute(base_stmt)
        items = items_result.scalars().all()

        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar_one()

        return items, total

    async def acknowledge(self, alert_id: UUID, user_id: UUID) -> Optional[Alert]:
        """Acknowledge an alert."""
        alert = await self.get_by_id(alert_id)
        if alert and not alert.acknowledged:
            alert.acknowledged = True
            alert.acknowledged_by = user_id
            from datetime import timezone
            alert.acknowledged_at = datetime.now(timezone.utc)
            await self.db.flush()
        return alert

    async def get_summary_by_user(self, user_id: UUID) -> dict[str, Any]:
        """Retrieve alert summary for all sites owned by a user."""
        # Unacknowledged count
        unack_stmt = select(func.count()).select_from(Alert).join(Site).where(
            Site.user_id == user_id,
            Alert.acknowledged == False
        )
        unack_res = await self.db.execute(unack_stmt)
        unacknowledged_count = unack_res.scalar_one()

        # Latest critical alert
        latest_crit_stmt = select(Alert).join(Site).where(
            Site.user_id == user_id,
            Alert.severity == 'critical'
        ).order_by(Alert.created_at.desc()).limit(1)
        latest_crit_res = await self.db.execute(latest_crit_stmt)
        latest_critical = latest_crit_res.scalar_one_or_none()

        # Group by severity
        sev_stmt = select(Alert.severity, func.count()).join(Site).where(
            Site.user_id == user_id
        ).group_by(Alert.severity)
        sev_res = await self.db.execute(sev_stmt)
        by_severity = {row[0]: row[1] for row in sev_res.all()}

        # Group by alert type
        type_stmt = select(Alert.alert_type, func.count()).join(Site).where(
            Site.user_id == user_id
        ).group_by(Alert.alert_type)
        type_res = await self.db.execute(type_stmt)
        by_type = {row[0]: row[1] for row in type_res.all()}

        return {
            "by_severity": by_severity,
            "by_type": by_type,
            "unacknowledged_count": unacknowledged_count,
            "latest_critical": latest_critical
        }
