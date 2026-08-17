import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

_is_sqlite = settings.database_url.startswith("sqlite")

if _is_sqlite:
    _db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")
    if _db_path and not _db_path.startswith(":"):
        os.makedirs(os.path.dirname(os.path.abspath(_db_path)) or ".", exist_ok=True)
    engine = create_async_engine(settings.database_url, echo=False)
else:
    # Hosted Postgres (e.g. Neon) requires TLS; asyncpg wants `ssl=`, not libpq's
    # `sslmode`/`channel_binding` query params, so strip those and set it explicitly.
    from urllib.parse import urlsplit, urlunsplit

    parts = urlsplit(settings.database_url)
    db_url = urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    engine = create_async_engine(db_url, echo=False, connect_args={"ssl": "require"})

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
