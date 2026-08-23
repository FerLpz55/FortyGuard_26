import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.energy import EnergyConsumption
from app.schemas.energy import EnergyCreate, EnergyHistoryResponse
from app.repositories.base import BaseRepository

logger = structlog.get_logger(__name__)

class EnergyService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.energy_repo = BaseRepository[EnergyConsumption](EnergyConsumption, db)
        
    async def log_consumption(self, site_id: uuid.UUID, data: EnergyCreate) -> EnergyConsumption:
        logger.info("log_energy", site_id=str(site_id), kwh=data.kwh)
        create_data = data.model_dump()
        create_data["site_id"] = site_id
        return await self.energy_repo.create(**create_data)
        
    async def get_history(self, site_id: uuid.UUID, start, end, zone_id: Optional[str] = None, interval: str = "daily") -> EnergyHistoryResponse:
        # Placeholder implementation for missing specific EnergyRepository
        return EnergyHistoryResponse(
            site_id=site_id,
            interval=interval,
            data=[],
            stats={}
        )
