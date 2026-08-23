from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional

from app.api.deps import get_db, get_current_user
from app.services.energy_service import EnergyService
from app.schemas.energy import EnergyCreate, EnergyHistoryResponse, EnergyResponse
from app.models.user import User

router = APIRouter()

@router.get("/sites/{site_id}/energy/consumption", response_model=EnergyHistoryResponse)
async def get_energy_consumption(
    site_id: str,
    start: datetime,
    end: datetime,
    zone_id: Optional[str] = None,
    interval: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> EnergyHistoryResponse:
    """Get energy consumption history."""
    service = EnergyService(db)
    return await service.get_history(site_id, start, end, zone_id, interval)

@router.post("/sites/{site_id}/energy/consumption", response_model=EnergyResponse, status_code=status.HTTP_201_CREATED)
async def log_energy_consumption(
    site_id: str,
    data: EnergyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> EnergyResponse:
    """Log energy consumption."""
    service = EnergyService(db)
    return await service.log_consumption(site_id, data)

@router.get("/sites/{site_id}/energy/waste-analysis")
async def analyze_energy_waste(
    site_id: str,
    current_user: User = Depends(get_current_user)
) -> dict:
    """Analyze energy waste (deferred to agent)."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Agent endpoints deferred to BE-09/BE-10")
