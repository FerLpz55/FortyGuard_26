import uuid
from typing import Optional
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from app.core.database import get_db
from app.core.security import decode_token
from app.core.config import get_settings
from app.core.exceptions import AuthenticationError
from app.models.user import User
from app.repositories.user_repo import UserRepository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """
    Decode JWT, fetch user from DB, verify active.
    Raises 401 if any step fails.
    """
    try:
        payload = decode_token(token)
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise AuthenticationError("Token payload invalid")
            
        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(uuid.UUID(user_id_str))
        
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")
            
        return user
    except AuthenticationError:
        raise
    except JWTError as e:
        raise AuthenticationError("Could not validate credentials") from e
