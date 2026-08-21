from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


class EnergyConsumptionBase(BaseModel):
    zone_id: str | None = None
    kwh: float = Field(..., gt=0)
    cost_usd: float | None = None
    recorded_at: datetime
    metadata: dict = {}


class EnergyConsumptionCreate(EnergyConsumptionBase):
    pass


class EnergyConsumptionResponse(EnergyConsumptionBase):
    id: int
    site_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class EnergyConsumptionListResponse(BaseModel):
    site_id: UUID
    interval: str
    data: list[EnergyConsumptionResponse]
    totals: dict


class EnergyWasteFinding(BaseModel):
    zone_id: str
    issue: str
    description: str
    estimated_waste_kwh_day: float
    estimated_savings_usd_month: float
    confidence: float


class EnergyWasteAnalysisResponse(BaseModel):
    site_id: UUID
    analysis_period_days: int
    findings: list[EnergyWasteFinding]
    summary: dict