import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

class TemperatureReading(BaseModel):
    """Schema for an individual temperature reading."""
    site_id: uuid.UUID
    temperature_c: float = Field(..., ge=-50.0, le=80.0)
    humidity_pct: float = Field(..., ge=0.0, le=100.0)
    heat_index_c: float
    apparent_temp_c: float
    source: str = "fortyguard"
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TemperatureForecast(BaseModel):
    """Schema for a forecasted temperature data point."""
    timestamp: datetime
    temperature_c: float
    humidity_pct: float
    heat_index_c: float

class TemperatureStats(BaseModel):
    """Schema for aggregated temperature statistics."""
    min: float
    max: float
    avg: float
    p95: float

class TemperatureHistoryResponse(BaseModel):
    """Schema for returning historical temperature data."""
    site_id: uuid.UUID
    interval: str
    unit: str = "celsius"
    data: list[TemperatureReading]
    stats: TemperatureStats

class TemperatureStatsResponse(BaseModel):
    """Schema for aggregated KPI insights over a period."""
    site_id: uuid.UUID
    period: str
    temperature_c: TemperatureStats
    heat_index_c: TemperatureStats
    exceedance_hours: float = Field(..., description="Hours exceeding safe thresholds")
