from app.schemas.common import PaginationParams, PaginatedResponse, ErrorResponse, MessageResponse
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, TokenRefresh, TokenPayload
from app.schemas.site import SiteCreate, SiteUpdate, SiteResponse, SiteListResponse
from app.schemas.temperature import (
    TemperatureReadingResponse,
    TemperatureHistoryResponse,
    TemperatureForecastResponse,
    TemperatureStatsResponse,
)
from app.schemas.alert import AlertCreate, AlertUpdate, AlertResponse, AlertListResponse, AlertSummaryResponse
from app.schemas.energy import (
    EnergyConsumptionCreate,
    EnergyConsumptionResponse,
    EnergyConsumptionListResponse,
    EnergyWasteAnalysisResponse,
)
from app.schemas.agent import (
    AgentChatRequest,
    AgentChatResponse,
    AgentActionRequest,
    AgentActionResponse,
    AgentStatusResponse,
)

__all__ = [
    "PaginationParams",
    "PaginatedResponse",
    "ErrorResponse",
    "MessageResponse",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "Token",
    "TokenRefresh",
    "TokenPayload",
    "SiteCreate",
    "SiteUpdate",
    "SiteResponse",
    "SiteListResponse",
    "TemperatureReadingResponse",
    "TemperatureHistoryResponse",
    "TemperatureForecastResponse",
    "TemperatureStatsResponse",
    "AlertCreate",
    "AlertUpdate",
    "AlertResponse",
    "AlertListResponse",
    "AlertSummaryResponse",
    "EnergyConsumptionCreate",
    "EnergyConsumptionResponse",
    "EnergyConsumptionListResponse",
    "EnergyWasteAnalysisResponse",
    "AgentChatRequest",
    "AgentChatResponse",
    "AgentActionRequest",
    "AgentActionResponse",
    "AgentStatusResponse",
]