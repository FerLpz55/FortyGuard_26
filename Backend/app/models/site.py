import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import String, text, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.models.base import Base

class Site(Base):
    """
    Site model representing a physical location monitored by FortyGuard.
    """
    __tablename__ = "sites"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=True)
    
    lat: Mapped[float] = mapped_column(Numeric(10, 8), nullable=False)
    lon: Mapped[float] = mapped_column(Numeric(11, 8), nullable=False)
    
    site_type: Mapped[str] = mapped_column(String(50), nullable=False)
    metadata_: Mapped[dict[str, Any]] = mapped_column(JSONB, server_default='{}', nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sites")
    temperature_readings: Mapped[list["TemperatureReading"]] = relationship("TemperatureReading", back_populates="site", cascade="all, delete-orphan")
    alerts: Mapped[list["Alert"]] = relationship("Alert", back_populates="site", cascade="all, delete-orphan")
    agent_actions: Mapped[list["AgentAction"]] = relationship("AgentAction", back_populates="site", cascade="all, delete-orphan")
    energy_consumption: Mapped[list["EnergyConsumption"]] = relationship("EnergyConsumption", back_populates="site", cascade="all, delete-orphan")
