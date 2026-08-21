from typing import Optional, Literal
from pydantic import BaseModel, Field
from uuid import UUID


class AgentChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    site_id: UUID | None = None
    session_id: UUID | None = None


class AgentActionTaken(BaseModel):
    tool: str
    params: dict
    result: str


class AgentChatResponse(BaseModel):
    session_id: UUID
    response: dict
    metadata: dict


class AgentActionRequest(BaseModel):
    action: str
    params: dict = {}


class AgentActionResponse(BaseModel):
    action_id: UUID
    status: str
    result: dict
    execution_time_ms: int


class AgentStatusResponse(BaseModel):
    status: str
    last_scheduled_run: str | None
    last_user_query: str | None
    tools_available: int
    governance: dict
    trust_score: float