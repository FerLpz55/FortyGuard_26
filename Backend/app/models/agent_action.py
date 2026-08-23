import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import String, text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.models.base import Base

class AgentAction(Base):
    """
    Agent Action model to keep an audit trail of AI automated actions.
    """
    __tablename__ = "agent_actions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    site_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sites.id", ondelete="SET NULL"), nullable=True)
    
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    trigger: Mapped[str] = mapped_column(String(255), nullable=False)
    
    input_data: Mapped[dict[str, Any]] = mapped_column(JSONB, server_default='{}', nullable=False)
    output_data: Mapped[dict[str, Any]] = mapped_column(JSONB, server_default='{}', nullable=False)
    
    status: Mapped[str] = mapped_column(String(50), default="success", nullable=False)
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
    execution_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"), nullable=False)

    # Relationships
    site: Mapped["Site"] = relationship("Site", back_populates="agent_actions")
