from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.api.deps import get_db, get_current_user
from app.services.site_service import SiteService
from app.schemas.site import SiteCreate, SiteUpdate, SiteResponse
from app.schemas.common import PaginatedResponse
from app.models.user import User

router = APIRouter()

@router.get("", response_model=PaginatedResponse)
async def get_all_sites(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> PaginatedResponse:
    """Retrieve a paginated list of sites for the current user."""
    service = SiteService(db)
    return await service.get_all_for_user(current_user.id, page, size)

@router.post("", response_model=SiteResponse, status_code=status.HTTP_201_CREATED)
async def create_site(
    data: SiteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SiteResponse:
    """Create a new site."""
    service = SiteService(db)
    return await service.create(current_user.id, data)

@router.get("/{site_id}", response_model=SiteResponse)
async def get_site(
    site_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SiteResponse:
    """Retrieve a specific site by ID."""
    service = SiteService(db)
    return await service.get(site_id, current_user.id)

@router.patch("/{site_id}", response_model=SiteResponse)
async def update_site(
    site_id: str,
    data: SiteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> SiteResponse:
    """Update a specific site by ID."""
    service = SiteService(db)
    return await service.update(site_id, current_user.id, data)

@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site(
    site_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """Delete a specific site by ID."""
    service = SiteService(db)
    await service.delete(site_id, current_user.id)
