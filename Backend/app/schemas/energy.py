import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field, ConfigDict

class EnergyCreate(BaseModel):
    """Schema for creating a new energy consumption reading."""
    zone_id: str | None = Field(None, max_length=100)
    kwh: float = Field(..., ge=0.0)
    cost_usd: float = Field(..., ge=0.0)
    recorded_at: datetime
    metadata_: dict[str, Any] = Field(default_factory=dict)

class EnergyResponse(EnergyCreate):
    """Schema for returning energy reading data."""
    id: int
    site_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EnergyHistoryResponse(BaseModel):
    """Schema for returning historical energy consumption aggregated."""
    site_id: uuid.UUID
    interval: str
    data: list[EnergyResponse]
    totals: dict[str, float] = Field(description="Aggregated totals, e.g. total_kwh, total_cost")
