import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import structlog

from app.core.config import get_settings
from app.core.database import async_session_maker
from app.repositories.site_repo import SiteRepository
# Removed circular import of TemperatureService
from app.services.agent_service import AgentService
from app.integrations.fortyguard import FortyGuardNoCoverage

logger = structlog.get_logger(__name__)

scheduler = AsyncIOScheduler()

async def poll_all_sites() -> None:
    """Fetch and store data for all active sites, trigger alerts & agents if needed."""
    logger.info("polling_all_sites_started")
    
    # We create a new DB session for the scheduled task
    async with async_session_maker() as db:
        from app.repositories.site_repo import SiteRepository
        from app.services.temperature_service import TemperatureService
        from app.services.agent_service import AgentService
        from app.integrations.fortyguard import FortyGuardClient
        
        site_repo = SiteRepository(db)
        temp_service = TemperatureService(db)
        agent_service = AgentService(db)
        
        sites = await site_repo.get_all_active()
        logger.info("scheduler_start", site_count=len(sites))
        
        client = FortyGuardClient()
        try:
            for site in sites:
                try:
                    reading = await temp_service.fetch_and_store(site, client)
                    # Agent decision logic can happen here if needed later (Phase 2)
                except Exception as e:
                    logger.error("scheduler_site_error", site_id=str(site.id), error=str(e))
        finally:
            await client.close()
            
        await db.commit()
                
    logger.info("polling_all_sites_completed")

def start_scheduler() -> None:
    """Initialize and start the background task scheduler."""
    settings = get_settings()
    interval = settings.scheduler_interval_minutes
    
    scheduler.add_job(poll_all_sites, 'interval', minutes=interval, id='poll_sites_job', replace_existing=True)
    scheduler.start()
    logger.info("scheduler_started", interval_minutes=interval)

def stop_scheduler() -> None:
    """Gracefully shutdown the scheduler."""
    scheduler.shutdown()
    logger.info("scheduler_stopped")
