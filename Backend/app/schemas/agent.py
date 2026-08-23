import uuid
from typing import Any
from pydantic import BaseModel, Field, ConfigDict

class AgentChatRequest(BaseModel):
    """Schema for user messages to the AI Agent."""
    message: str = Field(..., min_length=1, max_length=2000, description="User prompt")
    site_id: uuid.UUID | None = Field(None, description="Optional site context")
    session_id: str | None = Field(None, description="Session ID for conversation continuity")

class AgentChatResponse(BaseModel):
    """Schema for agent responses."""
    response: str = Field(description="Agent text response")
    actions_taken: list[dict[str, Any]] | None = Field(default=None, description="Automated actions triggered")
    session_id: str = Field(description="Session ID for continuity")

class AgentActionRequest(BaseModel):
    """Schema for invoking a specific agent action."""
    action: str = Field(..., max_length=100)
    params: dict[str, Any] = Field(default_factory=dict)

class AgentActionResponse(BaseModel):
    """Schema for agent action execution result."""
    id: uuid.UUID
    status: str
    result: dict[str, Any]
    error: str | None = None
