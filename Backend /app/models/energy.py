from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, Numeric, ForeignKey, JSON, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.site import Site


class EnergyConsumption(Base):
    __tablename__ = "energy_consumption"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    site_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    zone_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    kwh: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    cost_usd: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    metadata: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    site: Mapped["Site"] = relationship(back_populates="energy_consumption")

    __table_args__ = (
        Index("idx_energy_site_time", "site_id", "recorded_at", postgresql_using="btree"),
    )