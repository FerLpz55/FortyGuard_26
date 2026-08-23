from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.energy import EnergyConsumption

class EnergyRepository(BaseRepository):
    async def get_history(self, site_id: int, limit: int = 100):
        """
        Obtiene el historial de consumo de energía para un sitio específico,
        ordenado por fecha de forma descendente.
        """
        query = (
            select(EnergyConsumption)
            .where(EnergyConsumption.site_id == site_id)
            .order_by(EnergyConsumption.recorded_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()