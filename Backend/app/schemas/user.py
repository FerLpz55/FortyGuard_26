from datetime import datetime
import uuid
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="Strong password")
    full_name: str | None = Field(None, max_length=255, description="User's full name")

class UserLogin(BaseModel):
    """Schema for user login credentials."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

class UserResponse(BaseModel):
    """Schema for returning user data."""
    id: uuid.UUID
    email: str
    full_name: str | None
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = Field(description="Access token expiration in seconds")
    user: UserResponse

class TokenRefreshResponse(BaseModel):
    """Schema for refreshed token response."""
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
