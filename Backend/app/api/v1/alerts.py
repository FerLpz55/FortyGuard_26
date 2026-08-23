from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid
from typing import Optional

from app.api.deps import get_db, get_current_user
from app.services.alert_service import AlertService
from app.schemas.common import PaginatedResponse
from app.schemas.alert import AlertResponse, AlertSummary
from app.models.user import User

router = APIRouter()

@router.get("/sites/{site_id}/alerts", response_model=PaginatedResponse)
async def get_site_alerts(
    site_id: uuid.UUID,
    severity: Optional[str] = None,
    alert_type: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> PaginatedResponse:
    """Get alerts for a site."""
    service = AlertService(db)
    filters = {
        "severity": severity,
        "alert_type": alert_type,
        "acknowledged": acknowledged,
        "start": start,
        "end": end
    }
    # Clean up None values
    filters = {k: v for k, v in filters.items() if v is not None}
    return await service.get_by_site(site_id, current_user.id, filters=filters, page=page, size=size)

@router.patch("/alerts/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> AlertResponse:
    """Acknowledge an alert."""
    service = AlertService(db)
    return await service.acknowledge(alert_id, current_user.id)

@router.get("/alerts/summary", response_model=AlertSummary)
async def get_alerts_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> AlertSummary:
    """Get alert summary for user."""
    service = AlertService(db)
    return await service.get_summary(current_user.id)
