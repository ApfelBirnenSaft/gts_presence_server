import json
import logging
from sqlalchemy import URL, event
from sqlmodel import SQLModel, main
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from typing import AsyncGenerator, Type
from sqlalchemy.orm import Session as SASession

from . import versioning
import utils

setattr(SQLModel, 'registry', main.default_registry)

database_url = URL.create("mysql+aiomysql", "gtsv2", "k4xB7wP8zrEwfapM", "localhost", 3306, "gtsv2", {"charset": "utf8mb4"})

engine: AsyncEngine = create_async_engine(database_url, echo=False, pool_pre_ping=True)

async_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

async def create_db_and_tables():
    import api.models as models

    versioning.create_all_version_models(models)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    print(models.employee)


@event.listens_for(SASession, "after_flush")
def before_flush(session:SASession, flush_context):#, instances):
    print("After flush triggered")
    def make_version(obj, operation:versioning.Operation):
        if issubclass(type(obj), versioning.VersionedMixin):
            v_cls: Type[versioning.VersionModelMixin] = obj.get_version_class()
            data: dict = obj.model_dump()
            exclude_fields = getattr(obj, "__version_exclude_fields__", [])
            for field in exclude_fields:
                data.pop(field, None)
            v_cls = obj.get_version_class()
            v_instance = v_cls(
                version_operation=operation,
                **data,
            )
            session.add(v_instance)
    for obj in session.new:
        make_version(obj, versioning.Operation.INSERT)
    for obj in session.dirty:
        make_version(obj, versioning.Operation.UPDATE)
    for obj in session.deleted:
        make_version(obj, versioning.Operation.DELETE)
