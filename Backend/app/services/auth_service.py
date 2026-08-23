import uuid
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, TokenResponse, TokenRefreshResponse, UserResponse
from app.repositories.user_repo import UserRepository
from app.core.exceptions import ConflictError, AuthenticationError
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.config import get_settings

logger = structlog.get_logger(__name__)

class AuthService:
    """Service handling user registration, authentication and token refresh."""
    
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.settings = get_settings()

    async def register(self, data: UserCreate) -> TokenResponse:
        """Register a new user."""
        existing_user = await self.user_repo.get_by_email(data.email)
        if existing_user:
            logger.warning("registration_failed", reason="email_taken", email=data.email)
            raise ConflictError("Email already registered")
        
        hashed_password = hash_password(data.password)
        
        user = await self.user_repo.create(
            email=data.email,
            password_hash=hashed_password,
            full_name=data.full_name,
            is_active=True,
            role="user"
        )
        
        logger.info("user_registered", user_id=str(user.id))
        return self._generate_tokens(user)
        
    async def login(self, data: UserLogin) -> TokenResponse:
        """Authenticate user and return tokens."""
        user = await self.user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            logger.warning("login_failed", reason="invalid_credentials", email=data.email)
            raise AuthenticationError("Invalid email or password")
            
        if not user.is_active:
            logger.warning("login_failed", reason="user_inactive", user_id=str(user.id))
            raise AuthenticationError("User is inactive")
            
        logger.info("user_logged_in", user_id=str(user.id))
        return self._generate_tokens(user)

    async def refresh_token(self, refresh_token: str) -> TokenRefreshResponse:
        """Issue new access token using refresh token."""
        try:
            payload = decode_token(refresh_token)
        except AuthenticationError:
            logger.warning("token_refresh_failed", reason="invalid_token")
            raise AuthenticationError("Invalid refresh token")

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise AuthenticationError("Invalid refresh token payload")
            
        user = await self.user_repo.get_by_id(uuid.UUID(user_id_str))
        if not user or not user.is_active:
            logger.warning("token_refresh_failed", reason="user_not_found_or_inactive", user_id=user_id_str)
            raise AuthenticationError("User not found or inactive")
            
        access_token = create_access_token({"sub": str(user.id)})
        return TokenRefreshResponse(
            access_token=access_token,
            expires_in=self.settings.access_token_expire_minutes * 60
        )

    def _generate_tokens(self, user: User) -> TokenResponse:
        """Helper to generate JWT tokens and response schema."""
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        user_response = UserResponse.model_validate(user)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.settings.access_token_expire_minutes * 60,
            user=user_response
        )
