from typing import Optional, Sequence, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.temperature import TemperatureReading
from app.repositories.base import BaseRepository

class TemperatureRepository(BaseRepository[TemperatureReading]):
    """Repository for TemperatureReading model operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(TemperatureReading, db)

    async def get_latest_by_site(self, site_id: UUID) -> Optional[TemperatureReading]:
        """Retrieve the most recent temperature reading for a site."""
        stmt = select(TemperatureReading).where(
            TemperatureReading.site_id == site_id
        ).order_by(TemperatureReading.recorded_at.desc()).limit(1)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_history(self, site_id: UUID, start: datetime, end: datetime) -> Sequence[TemperatureReading]:
        """Retrieve temperature readings for a site within a time range."""
        stmt = select(TemperatureReading).where(
            TemperatureReading.site_id == site_id,
            TemperatureReading.recorded_at >= start,
            TemperatureReading.recorded_at <= end
        ).order_by(TemperatureReading.recorded_at.asc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_stats(self, site_id: UUID, start: datetime, end: datetime) -> dict[str, Any]:
        """Calculate minimum, maximum, and average temperatures for a site within a time range."""
        stmt = select(
            func.min(TemperatureReading.temperature_c).label('min_temp'),
            func.max(TemperatureReading.temperature_c).label('max_temp'),
            func.avg(TemperatureReading.temperature_c).label('avg_temp')
        ).where(
            TemperatureReading.site_id == site_id,
            TemperatureReading.recorded_at >= start,
            TemperatureReading.recorded_at <= end
        )
        result = await self.db.execute(stmt)
        row = result.one_or_none()
        if not row or row.min_temp is None:
            return {"min": None, "max": None, "avg": None}
        return {
            "min": float(row.min_temp),
            "max": float(row.max_temp),
            "avg": float(row.avg_temp)
        }

    async def bulk_create(self, readings: list[dict[str, Any]]) -> int:
        """Efficiently create multiple temperature readings."""
        if not readings:
            return 0
        objects = [TemperatureReading(**reading) for reading in readings]
        self.db.add_all(objects)
        await self.db.flush()
        return len(objects)
