from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field
from uuid import UUID


AlertType = Literal["heat_risk", "energy_waste", "worker_safety", "anomaly"]
Severity = Literal["info", "warning", "critical"]


class AlertBase(BaseModel):
    site_id: UUID
    alert_type: AlertType
    severity: Severity
    title: str = Field(..., min_length=1, max_length=255)
    message: str | None = None
    metadata: dict = {}


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    acknowledged: bool


class AlertResponse(AlertBase):
    id: UUID
    acknowledged: bool
    acknowledged_by: UUID | None
    acknowledged_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    items: list[AlertResponse]
    total: int
    page: int
    size: int
    pages: int


class AlertSummaryResponse(BaseModel):
    by_severity: dict[str, int]
    by_type: dict[str, int]
    unacknowledged_count: int
    latest_critical: dict | None