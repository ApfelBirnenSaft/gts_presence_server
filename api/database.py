from sqlalchemy import URL
from sqlmodel import SQLModel, main
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from typing import AsyncGenerator

database_url = URL.create("mysql+aiomysql", "gtsv2", "k4xB7wP8zrEwfapM", "localhost", 3306, "gtsv2", {"charset": "utf8mb4"})

engine: AsyncEngine = create_async_engine(database_url, echo=True, pool_pre_ping=True)

async_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
