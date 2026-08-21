from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import String, Numeric, ForeignKey, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.site import Site


class TemperatureReading(Base):
    __tablename__ = "temperature_readings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    site_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    temperature_c: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    humidity_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    heat_index_c: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    apparent_temp_c: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="fortyguard")
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    site: Mapped["Site"] = relationship(back_populates="temperature_readings")

    __table_args__ = (
        Index("idx_temp_site_time", "site_id", "recorded_at", postgresql_using="btree"),
        Index("idx_temp_recorded", "recorded_at"),
    )