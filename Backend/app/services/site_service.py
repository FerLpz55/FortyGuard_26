import uuid
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.site import Site
from app.schemas.site import SiteCreate, SiteUpdate, SiteResponse
from app.schemas.common import PaginatedResponse
from app.repositories.site_repo import SiteRepository
from app.core.exceptions import AuthorizationError, NotFoundError

logger = structlog.get_logger(__name__)

class SiteService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.site_repo = SiteRepository(db)
    
    async def create(self, user_id: uuid.UUID, data: SiteCreate) -> Site:
        logger.info("site_create", user_id=str(user_id), name=data.name)
        create_data = data.model_dump()
        create_data["user_id"] = user_id
        return await self.site_repo.create(**create_data)
        
    async def get_all_for_user(self, user_id: uuid.UUID, page: int = 1, size: int = 10) -> PaginatedResponse[SiteResponse]:
        skip = (page - 1) * size
        sites = await self.site_repo.get_by_user(user_id, skip=skip, limit=size)
        total = await self.site_repo.count_by_user(user_id)
        pages = (total + size - 1) // size
        return PaginatedResponse(
            items=[SiteResponse.model_validate(s) for s in sites],
            total=total,
            page=page,
            size=size,
            pages=pages
        )

    async def get(self, site_id: uuid.UUID, user_id: uuid.UUID) -> Site:
        site = await self.site_repo.get_by_id_and_user(site_id, user_id)
        if not site:
            raise NotFoundError("Site not found")
        
        if site.user_id != user_id:
            logger.warning("unauthorized_site_access", user_id=str(user_id), site_id=str(site_id))
            raise AuthorizationError("Not authorized to access this site")
            
        return site

    async def update(self, site_id: uuid.UUID, user_id: uuid.UUID, data: SiteUpdate) -> Site:
        site = await self.get(site_id, user_id)
        update_data = data.model_dump(exclude_unset=True)
        updated_site = await self.site_repo.update(site.id, **update_data)
        if not updated_site:
            raise NotFoundError("Failed to update site")
        return updated_site

    async def delete(self, site_id: uuid.UUID, user_id: uuid.UUID) -> None:
        site = await self.get(site_id, user_id)
        if hasattr(site, 'is_active'):
            await self.site_repo.update(site.id, is_active=False)
        else:
            await self.site_repo.delete(site.id)
