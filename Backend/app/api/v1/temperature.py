from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional

from app.api.deps import get_db, get_current_user
from app.services.temperature_service import TemperatureService
from app.schemas.temperature import TemperatureReading, TemperatureHistoryResponse, TemperatureStatsResponse
from app.models.user import User

router = APIRouter()

@router.get("/sites/{site_id}/temperature/latest", response_model=Optional[TemperatureReading])
async def get_latest_temperature(
    site_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Optional[TemperatureReading]:
    """Get the latest temperature reading for a site."""
    service = TemperatureService(db)
    return await service.get_latest(site_id)

@router.get("/sites/{site_id}/temperature/history", response_model=TemperatureHistoryResponse)
async def get_temperature_history(
    site_id: str,
    start: datetime,
    end: datetime,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TemperatureHistoryResponse:
    """Get temperature history for a site within a date range."""
    service = TemperatureService(db)
    return await service.get_history(site_id, start, end)

@router.get("/sites/{site_id}/temperature/stats", response_model=TemperatureStatsResponse)
async def get_temperature_stats(
    site_id: str,
    start: datetime,
    end: datetime,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TemperatureStatsResponse:
    """Get temperature stats for a site within a date range."""
    service = TemperatureService(db)
    return await service.get_stats(site_id, start, end)

@router.get("/sites/{site_id}/temperature/forecast")
async def get_temperature_forecast(
    site_id: str,
    current_user: User = Depends(get_current_user)
) -> dict:
    """Get temperature forecast (Not implemented)."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not Implemented")
