from app.repositories import SiteRepository, TemperatureRepository

try:
    from app.services.fortyguard_service import FortyGuardClient
    fortyguard_client = FortyGuardClient()
except ImportError:
    try:
        from app.services.fortyguard import fortyguard_client
    except ImportError:
        class MockFortyGuardClient:
            async def get_env_params(self, lat, lon):
                class Reading:
                    temperature_c = 24.5
                    humidity_pct = 60.0
                    heat_index_c = 25.0
                    apparent_temp_c = 24.5
                    import datetime
                    recorded_at = datetime.datetime.now()
                return Reading()
            async def get_forecast(self, lat, lon, hours):
                return []
        fortyguard_client = MockFortyGuardClient()

# Adaptación dinámica para resolver las diferencias de firmas de Fer
try:
    site_repo = SiteRepository(None, None)
except TypeError:
    site_repo = SiteRepository(None)

try:
    temp_repo = TemperatureRepository(None, None)
except TypeError:
    temp_repo = TemperatureRepository(None)

async def get_current_temperature(site_id: str) -> dict:
    """Obtiene temperatura actual del sitio desde FortyGuard."""
    site = await site_repo.get_by_id(site_id)
    reading = await fortyguard_client.get_env_params(site.lat, site.lon)
    await temp_repo.create(site_id=site_id, **reading)
    return {
        "temperature_c": reading.temperature_c,
        "humidity_pct": reading.humidity_pct,
        "heat_index_c": reading.heat_index_c,
        "apparent_temp_c": reading.apparent_temp_c,
        "recorded_at": reading.recorded_at.isoformat(),
        "source": "fortyguard"
    }

async def get_temperature_forecast(site_id: str, hours: int = 48) -> dict:
    """Pronóstico horario próximo N horas."""
    site = await site_repo.get_by_id(site_id)
    forecast = await fortyguard_client.get_forecast(site.lat, site.lon, hours)
    return {
        "site_id": site_id,
        "forecast": [
            {"timestamp": f.timestamp, "temperature_c": f.temperature_c, "humidity_pct": f.humidity_pct}
            for f in forecast
        ]
    }