import uuid
from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field, ConfigDict

AlertType = Literal["heat_risk", "energy_waste", "worker_safety", "anomaly"]
AlertSeverity = Literal["info", "warning", "critical"]

class AlertCreate(BaseModel):
    """Schema for creating a new alert."""
    site_id: uuid.UUID
    alert_type: AlertType
    severity: AlertSeverity
    title: str = Field(..., max_length=255)
    message: str
    metadata_: dict[str, Any] = Field(default_factory=dict)

class AlertResponse(AlertCreate):
    """Schema for returning alert data."""
    id: uuid.UUID
    acknowledged: bool
    acknowledged_by: uuid.UUID | None
    acknowledged_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AlertAcknowledge(BaseModel):
    """Schema for acknowledging an alert."""
    acknowledged: bool = True

class AlertSummary(BaseModel):
    """Schema for returning summary of alerts."""
    by_severity: dict[AlertSeverity, int]
    by_type: dict[AlertType, int]
    unacknowledged_count: int
    latest_critical: AlertResponse | None
