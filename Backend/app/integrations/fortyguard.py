import asyncio
import httpx
import structlog
from typing import Any
from types import SimpleNamespace

from app.core.config import get_settings

logger = structlog.get_logger(__name__)

class FortyGuardError(Exception):
    """Base exception for FortyGuard API errors"""
    pass

class FortyGuardTaskFailed(FortyGuardError):
    """Raised when an async task explicitly fails on the API side"""
    pass

class FortyGuardTaskTimeout(FortyGuardError):
    """Raised when waiting for a task exceeds max wait time"""
    pass

class FortyGuardNoCoverage(FortyGuardError):
    """Raised when the location has no data coverage (404)"""
    pass

class FortyGuardClient:
    """Async HTTP Client for FortyGuard API."""
    
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = self.settings.fortyguard_base_url
        self.api_key = self.settings.fortyguard_api_key
        self.poll_interval = self.settings.fortyguard_poll_interval
        self.max_wait = self.settings.fortyguard_max_wait
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=10.0
        )

    async def close(self) -> None:
        """Close the underlying HTTPX client."""
        await self.client.aclose()

    async def _submit_task(self, endpoint: str, payload: dict) -> str:
        """Submit a task to the API and return the activity ID."""
        response = await self.client.post(endpoint, json=payload)
        
        if response.status_code == 404:
            raise FortyGuardNoCoverage("No coverage for this location")
            
        response.raise_for_status()
        data = response.json()
        return data.get("activity_id")

    async def _poll_status(self, activity_id: str) -> dict:
        """Poll the API for the status of an activity."""
        response = await self.client.get(f"/api/v1/activities/{activity_id}")
        response.raise_for_status()
        return response.json()

    async def submit_and_wait(self, endpoint: str, payload: dict) -> dict:
        """Submit a task and poll until completion or timeout."""
        activity_id = await self._submit_task(endpoint, payload)
        
        loop = asyncio.get_event_loop()
        start_time = loop.time()
        
        while (loop.time() - start_time) < self.max_wait:
            status_data = await self._poll_status(activity_id)
            status = status_data.get("status")
            
            if status == "completed":
                return status_data.get("result", {})
            elif status == "failed":
                raise FortyGuardTaskFailed(f"Task failed: {status_data.get('error')}")
                
            await asyncio.sleep(self.poll_interval)
            
        raise FortyGuardTaskTimeout(f"Task {activity_id} timed out after {self.max_wait} seconds")

    async def get_env_params(self, lat: float, lon: float, date: str) -> Any:
        """Retrieve environmental parameters for a given location and date."""
        payload = {"lat": lat, "lon": lon, "date": date}
        result = await self.submit_and_wait("/api/v1/env-params", payload)
        return self._parse_env_params(result)

    def _parse_env_params(self, result: dict) -> Any:
        """Helper to convert API response to an object with required fields."""
        return SimpleNamespace(
            temperature_c=result.get("temperature_c", 0.0),
            humidity_pct=result.get("humidity_pct", 0.0),
            heat_index_c=result.get("heat_index_c", 0.0),
            apparent_temp_c=result.get("apparent_temp_c", 0.0)
        )

    async def get_heatmap(self, lat: float, lon: float, date: str) -> dict:
        payload = {"lat": lat, "lon": lon, "date": date}
        return await self.submit_and_wait("/api/v1/heatmap", payload)

    async def get_exceedance_map(self, lat: float, lon: float, threshold: float, date: str) -> dict:
        payload = {"lat": lat, "lon": lon, "threshold": threshold, "date": date}
        return await self.submit_and_wait("/api/v1/exceedance-map", payload)

    async def get_api_usage(self) -> dict:
        response = await self.client.get("/api/v1/usage")
        response.raise_for_status()
        return response.json()
