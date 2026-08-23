import uuid
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertResponse, AlertSummary
from app.schemas.common import PaginatedResponse
from app.repositories.alert_repo import AlertRepository
from app.core.exceptions import NotFoundError, AuthorizationError
from app.models.site import Site

logger = structlog.get_logger(__name__)

class AlertService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.alert_repo = AlertRepository(db)
    
    async def get_by_site(self, site_id: uuid.UUID, page: int = 1, size: int = 10, **filters) -> PaginatedResponse[AlertResponse]:
        skip = (page - 1) * size
        alerts, total = await self.alert_repo.get_by_site(site_id, skip=skip, limit=size, **filters)
        pages = (total + size - 1) // size
        return PaginatedResponse(
            items=[AlertResponse.model_validate(a) for a in alerts],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
    async def acknowledge(self, alert_id: uuid.UUID, user_id: uuid.UUID) -> Alert:
        alert = await self.alert_repo.get_by_id(alert_id)
        if not alert:
            raise NotFoundError("Alert not found")
            
        # Access control verify if necessary (e.g. site ownership)
        
        updated_alert = await self.alert_repo.acknowledge(alert_id, user_id)
        if not updated_alert:
            raise NotFoundError("Failed to acknowledge alert")
            
        logger.info("alert_acknowledged", alert_id=str(alert_id), user_id=str(user_id))
        return updated_alert
        
    async def get_summary(self, user_id: uuid.UUID) -> AlertSummary:
        summary_dict = await self.alert_repo.get_summary_by_user(user_id)
        return AlertSummary(**summary_dict)
        
    async def create_alert(self, data: AlertCreate) -> Alert:
        logger.info("alert_created", site_id=str(data.site_id), severity=data.severity)
        create_data = data.model_dump()
        return await self.alert_repo.create(**create_data)
