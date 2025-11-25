from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

from .config import settings

DATABASE_URL = settings.get_db_url()

engine = create_async_engine(url = DATABASE_URL)
async_session_make = async_sessionmaker(bind = engine, class_ = AsyncSession, expire_on_commit = False)

async def get_session():
    async with async_session_make() as session:
        try:
            yield session
        finally:
            await session.close()

class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True