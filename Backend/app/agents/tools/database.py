from app.repositories import SiteRepository, TemperatureRepository, AlertRepository

# Adaptación dinámica
try:
    site_repo = SiteRepository(None, None)
except TypeError:
    site_repo = SiteRepository(None)

try:
    temp_repo = TemperatureRepository(None, None)
except TypeError:
    temp_repo = TemperatureRepository(None)

try:
    alert_repo = AlertRepository(None, None)
except TypeError:
    alert_repo = AlertRepository(None)

async def query_site_data(site_id: str) -> dict:
    """Configuración completa del sitio para toma de decisiones."""
    site = await site_repo.get_by_id(site_id)
    latest_temp = await temp_repo.get_latest(site_id)
    thresholds = site.metadata.get("heat_threshold_c", 35.0)
    hvac_config = site.metadata.get("hvac_config", {})
    return {
        "site_id": site_id,
        "name": site.name,
        "site_type": site.site_type,
        "coordinates": {"lat": site.lat, "lon": site.lon},
        "thresholds": {"heat_threshold_c": thresholds},
        "hvac_config": hvac_config,
        "latest_temperature": latest_temp,
        "operating_hours": site.metadata.get("operating_hours")
    }

async def create_alert(
    site_id: str,
    alert_type: str,
    severity: str,
    title: str,
    message: str,
    metadata: dict = None
) -> dict:
    """Crea alerta en BD y retorna ID."""
    alert = await alert_repo.create(
        site_id=site_id,
        alert_type=alert_type,
        severity=severity,
        title=title,
        message=message,
        metadata=metadata or {}
    )
    return {"alert_id": str(alert.id), "created_at": alert.created_at.isoformat()}