import uuid
from datetime import datetime

from sqlalchemy import String, text, DateTime, ForeignKey, Numeric, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Index

from app.models.base import Base

class TemperatureReading(Base):
    """
    Temperature Reading model for storing time-series thermal data.
    """
    __tablename__ = "temperature_readings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    site_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    
    temperature_c: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    humidity_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    heat_index_c: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    apparent_temp_c: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    
    source: Mapped[str] = mapped_column(String(50), default="fortyguard", nullable=False)
    
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)

    # Relationships
    site: Mapped["Site"] = relationship("Site", back_populates="temperature_readings")

    __table_args__ = (
        Index('idx_temp_site_time', 'site_id', text('recorded_at DESC')),
    )
