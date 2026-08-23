import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field, ConfigDict

class SiteBase(BaseModel):
    """Base schema for Site properties."""
    name: str = Field(..., max_length=255, description="Name of the site")
    address: str | None = Field(None, description="Physical address")
    lat: float = Field(..., ge=-90.0, le=90.0, description="Latitude")
    lon: float = Field(..., ge=-180.0, le=180.0, description="Longitude")
    site_type: str = Field(..., max_length=50, description="Type of site (e.g., construction, warehouse)")
    metadata_: dict[str, Any] = Field(default_factory=dict, description="Additional properties as JSON")

class SiteCreate(SiteBase):
    """Schema for creating a site."""
    pass

class SiteUpdate(BaseModel):
    """Schema for updating a site (all fields optional)."""
    name: str | None = Field(None, max_length=255)
    address: str | None = None
    lat: float | None = Field(None, ge=-90.0, le=90.0)
    lon: float | None = Field(None, ge=-180.0, le=180.0)
    site_type: str | None = Field(None, max_length=50)
    metadata_: dict[str, Any] | None = None

class SiteResponse(SiteBase):
    """Schema for returning site data."""
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
