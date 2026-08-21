from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID


class SiteBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    address: str | None = None
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    site_type: str | None = None
    metadata: dict = {}


class SiteCreate(SiteBase):
    pass


class SiteUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    address: str | None = None
    lat: float | None = Field(None, ge=-90, le=90)
    lon: float | None = Field(None, ge=-180, le=180)
    site_type: str | None = None
    metadata: dict | None = None


class SiteResponse(SiteBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SiteListResponse(BaseModel):
    items: list[SiteResponse]
    total: int
    page: int
    size: int
    pages: int