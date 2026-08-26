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
        from app.repositories.site_repo import SiteRepository
        self.site_repo = SiteRepository(db)
        from app.core.exceptions import NotFoundError, AuthorizationError
        self.AuthorizationError = AuthorizationError
        self.NotFoundError = NotFoundError
        
    async def _verify_ownership(self, site_id: uuid.UUID, user_id: uuid.UUID):
        site = await self.site_repo.get_by_id_and_user(site_id, user_id)
        if not site:
            raise self.NotFoundError("Site not found or not owned by user")
        
    async def fetch_and_store(self, site: Site, client: FortyGuardClient) -> TemperatureReading:
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
            
    async def get_latest(self, site_id: uuid.UUID, user_id: uuid.UUID) -> Optional[TemperatureReading]:
        await self._verify_ownership(site_id, user_id)
        return await self.temp_repo.get_latest_by_site(site_id)
        
    async def get_history(self, site_id: uuid.UUID, user_id: uuid.UUID, start: datetime, end: datetime) -> list[TemperatureReading]:
        await self._verify_ownership(site_id, user_id)
        return list(await self.temp_repo.get_history(site_id, start, end))
        
    async def get_stats(self, site_id: uuid.UUID, user_id: uuid.UUID, start: datetime, end: datetime) -> dict:
        await self._verify_ownership(site_id, user_id)
        return await self.temp_repo.get_stats(site_id, start, end)
