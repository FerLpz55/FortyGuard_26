from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


class TemperatureReadingBase(BaseModel):
    temperature_c: float = Field(..., ge=-50, le=80)
    humidity_pct: float | None = Field(None, ge=0, le=100)
    heat_index_c: float | None = None
    apparent_temp_c: float | None = None
    source: str = "fortyguard"


class TemperatureReadingResponse(TemperatureReadingBase):
    site_id: UUID
    recorded_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class TemperatureHistoryResponse(BaseModel):
    site_id: UUID
    interval: str
    unit: str
    data: list[dict]
    stats: dict


class TemperatureForecastResponse(BaseModel):
    site_id: UUID
    source: str
    generated_at: datetime
    forecast: list[dict]


class TemperatureStatsResponse(BaseModel):
    site_id: UUID
    period: dict
    temperature_c: dict
    heat_index_c: dict
    exceedance_hours: dict