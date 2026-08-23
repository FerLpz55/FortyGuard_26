from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, TokenRefreshResponse
from app.models.user import User
from app.core.exceptions import AppException

router = APIRouter()

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Register a new user."""
    try:
        service = AuthService(db)
        return await service.register(data)
    except AppException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Login a user and return access token."""
    try:
        service = AuthService(db)
        data = UserLogin(email=form_data.username, password=form_data.password)
        return await service.login(data)
    except AppException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
) -> TokenRefreshResponse:
    """Refresh an access token."""
    try:
        service = AuthService(db)
        return await service.refresh_token(refresh_token)
    except AppException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """Get current authenticated user."""
    return current_user
