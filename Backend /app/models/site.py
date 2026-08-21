import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, Text, Numeric, ForeignKey, JSON, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.temperature import TemperatureReading
    from app.models.alert import Alert
    from app.models.agent_action import AgentAction
    from app.models.energy import EnergyConsumption


class Site(Base):
    __tablename__ = "sites"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    lat: Mapped[float] = mapped_column(Numeric(10, 8), nullable=False)
    lon: Mapped[float] = mapped_column(Numeric(11, 8), nullable=False)
    site_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    metadata: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner: Mapped["User"] = relationship(back_populates="sites")
    temperature_readings: Mapped[list["TemperatureReading"]] = relationship(back_populates="site", cascade="all, delete-orphan")
    alerts: Mapped[list["Alert"]] = relationship(back_populates="site", cascade="all, delete-orphan")
    agent_actions: Mapped[list["AgentAction"]] = relationship(back_populates="site", cascade="all, delete-orphan")
    energy_consumption: Mapped[list["EnergyConsumption"]] = relationship(back_populates="site", cascade="all, delete-orphan")