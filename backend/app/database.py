from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator


from .config import settings



engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
)

async_session_maker = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an AsyncSession.
    Usage: db: AsyncSession = Depends(get_db)
    """
    async with async_session_maker() as session:
        yield session



async def test_connection() -> bool:
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        return bool(result.scalar())
