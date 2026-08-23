import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import String, text, DateTime, ForeignKey, Numeric, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Index

from app.models.base import Base

class EnergyConsumption(Base):
    """
    Energy Consumption model to track usage and cost.
    """
    __tablename__ = "energy_consumption"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    site_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    
    zone_id: Mapped[str] = mapped_column(String(100), nullable=True)
    kwh: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    cost_usd: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    metadata_: Mapped[dict[str, Any]] = mapped_column(JSONB, server_default='{}', nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)

    # Relationships
    site: Mapped["Site"] = relationship("Site", back_populates="energy_consumption")

    __table_args__ = (
        Index('idx_energy_site_time', 'site_id', 'recorded_at'),
    )
