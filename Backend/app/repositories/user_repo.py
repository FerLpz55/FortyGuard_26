from typing import Optional, Sequence
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email address."""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_users(self) -> Sequence[User]:
        """Retrieve all active users."""
        stmt = select(User).where(User.is_active == True)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def deactivate(self, user_id: UUID) -> Optional[User]:
        """Deactivate a user instead of hard deleting."""
        user = await self.get_by_id(user_id)
        if user and user.is_active:
            user.is_active = False
            await self.db.flush()
        return user
