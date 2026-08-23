from fastapi import APIRouter
from app.api.v1 import auth, sites, alerts, temperature, energy, agent

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(sites.router, prefix="/sites", tags=["Sites"])
api_v1_router.include_router(alerts.router, tags=["Alerts"])
api_v1_router.include_router(temperature.router, tags=["Temperature"])
api_v1_router.include_router(energy.router, tags=["Energy"])
api_v1_router.include_router(agent.router, prefix="/agent", tags=["Agent"])
