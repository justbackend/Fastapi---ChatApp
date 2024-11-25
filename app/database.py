from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.base import Base
from app.config import settings

engine = create_async_engine(
    settings.asyncpg_url.unicode_string(),
    future=True,
    echo=True,
)

AsyncSessionFactory = async_sessionmaker(
    engine,
    autoflush=False,
    expire_on_commit=False,
)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator:
    async with AsyncSessionFactory() as session:
        yield session


