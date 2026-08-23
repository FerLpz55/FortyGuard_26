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
        site_repo = SiteRepository(db)
        sites = await site_repo.get_all_active()
        
        from app.services.temperature_service import TemperatureService
        temp_service = TemperatureService(db)
        agent_service = AgentService(db)
        
        for site in sites:
            try:
                reading = await temp_service.fetch_and_store(site)
                
                # Retrieve threshold and evaluate
                metadata = getattr(site, "metadata_", {}) or {}
                heat_threshold_c = metadata.get("heat_threshold_c", 35.0)
                
                if reading.temperature_c > heat_threshold_c:
                    logger.info("heat_threshold_exceeded", site_id=str(site.id), temp=reading.temperature_c)
                    await agent_service.process_heat_alert(site.id, reading)
                    
            except FortyGuardNoCoverage:
                logger.warning("no_coverage_for_site", site_id=str(site.id))
            except Exception as e:
                # Catching any other exception so that a failure in one site does not crash the loop
                logger.error("error_polling_site", site_id=str(site.id), error=str(e))
                
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
