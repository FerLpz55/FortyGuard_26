"""Database engine and session factory.

Supports two modes:
- **Local dev**: Standard connection pool (pool_size + max_overflow).
- **Serverless / Supabase**: NullPool for PgBouncer transaction-mode
  compatibility. Supabase's connection pooler multiplexes connections,
  so SQLAlchemy must NOT maintain its own pool on top.

The mode is selected automatically based on the ENVIRONMENT setting.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings

settings = get_settings()

_is_serverless = settings.environment in ("production", "staging", "vercel")

# Supabase PgBouncer (transaction mode) requires NullPool — no client-side
# pooling on top of the server-side pooler.  For local dev we keep a pool.
_engine_kwargs: dict = {
    "echo": settings.environment == "development",
    "pool_pre_ping": True,
}

if _is_serverless:
    _engine_kwargs["poolclass"] = NullPool
else:
    _engine_kwargs["pool_size"] = settings.db_pool_size
    _engine_kwargs["max_overflow"] = settings.db_max_overflow

engine = create_async_engine(settings.database_url, **_engine_kwargs)

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a new SQLAlchemy AsyncSession.

    Ensures that the session is properly closed after the request is finished.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
