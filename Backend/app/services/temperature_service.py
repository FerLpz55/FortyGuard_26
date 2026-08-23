import uuid
from typing import Optional
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.temperature import TemperatureReading
from app.models.site import Site
from app.repositories.temperature_repo import TemperatureRepository
from app.repositories.alert_repo import AlertRepository
from app.integrations.fortyguard import FortyGuardClient
from app.core.exceptions import NotFoundError

logger = structlog.get_logger(__name__)

class TemperatureService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.temp_repo = TemperatureRepository(db)
        self.alert_repo = AlertRepository(db)
        
    async def fetch_and_store(self, site: Site) -> TemperatureReading:
        client = FortyGuardClient()
        try:
            today = date.today().isoformat()
            reading_data = await client.get_env_params(lat=site.lat, lon=site.lon, date=today)
            
            reading = await self.temp_repo.create(
                site_id=site.id,
                temperature_c=reading_data.temperature_c,
                humidity_pct=reading_data.humidity_pct,
                heat_index_c=reading_data.heat_index_c,
                apparent_temp_c=reading_data.apparent_temp_c,
                recorded_at=datetime.utcnow()
            )
            
            metadata = getattr(site, "metadata_", {}) or {}
            heat_threshold_c = metadata.get("heat_threshold_c", 35.0)
            
            if reading.temperature_c > heat_threshold_c:
                delta = reading.temperature_c - heat_threshold_c
                severity = "critical" if delta > 5 else ("high" if delta > 2 else "medium")
                
                await self.alert_repo.create(
                    site_id=site.id,
                    alert_type="high_temperature",
                    severity=severity,
                    message=f"Temperature {reading.temperature_c:.1f}°C exceeded threshold of {heat_threshold_c}°C",
                    data={"temperature_c": reading.temperature_c, "threshold": heat_threshold_c}
                )
            
            return reading
        finally:
            await client.close()
            
    async def get_latest(self, site_id: uuid.UUID) -> Optional[TemperatureReading]:
        return await self.temp_repo.get_latest_by_site(site_id)
        
    async def get_history(self, site_id: uuid.UUID, start: datetime, end: datetime) -> list[TemperatureReading]:
        return list(await self.temp_repo.get_history(site_id, start, end))
        
    async def get_stats(self, site_id: uuid.UUID, start: datetime, end: datetime) -> dict:
        return await self.temp_repo.get_stats(site_id, start, end)
