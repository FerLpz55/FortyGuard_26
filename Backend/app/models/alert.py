import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import String, text, DateTime, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Index

from app.models.base import Base

class Alert(Base):
    """
    Alert model representing triggered anomalies, heat risks, or safety warnings.
    """
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    site_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(String, nullable=False)
    
    metadata_: Mapped[dict[str, Any]] = mapped_column(JSONB, server_default='{}', nullable=False)
    
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    acknowledged_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)

    # Relationships
    site: Mapped["Site"] = relationship("Site", back_populates="alerts")
    acknowledged_by_user: Mapped["User"] = relationship("User", back_populates="alerts_acknowledged")

    __table_args__ = (
        Index('idx_alerts_site_time', 'site_id', 'created_at'),
        Index('idx_alerts_unacked', 'site_id', postgresql_where=text("acknowledged = false")),
    )
