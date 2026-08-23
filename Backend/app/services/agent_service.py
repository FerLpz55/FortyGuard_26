import uuid
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

logger = structlog.get_logger(__name__)

class AgentService:
    """Stub — full implementation deferred to BE-09/BE-10."""
    
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        
    async def process_heat_alert(self, site_id: uuid.UUID, reading) -> None:
        # Log the action, create alert, placeholder for agent logic
        logger.info("process_heat_alert_stub", site_id=str(site_id), temp=reading.temperature_c)
        pass
