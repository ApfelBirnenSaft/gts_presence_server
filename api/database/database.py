import inspect
from sqlalchemy import URL, event
from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from typing import AsyncGenerator
from sqlalchemy.orm import Session as SASession

from utils import dump_model_json, BaseDBModelWithId
from . import versioning

database_url = URL.create("mysql+aiomysql", "gtsv2", "k4xB7wP8zrEwfapM", "localhost", 3306, "gtsv2", {"charset": "utf8mb4"})

async_engine: AsyncEngine = create_async_engine(database_url, echo=False, pool_pre_ping=True)

async_session = async_sessionmaker(async_engine, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

async def create_all_tables():
    from api import models
    for name, cls in inspect.getmembers(models, inspect.isclass):
        if issubclass(cls, versioning.VersionedDBModel) and cls is not versioning.VersionedDBModel:
            cls.init_version_model()

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

@event.listens_for(SASession, "after_flush")
def before_flush(session:SASession, flush_context):#, instances):
    print("After flush triggered")
    def make_version(obj: BaseDBModelWithId, operation:versioning.Operation):
        obj_cls = type(obj)
        if issubclass(obj_cls, versioning.VersionedDBModel):
            v_cls = obj_cls.version_model()
            data: dict = dump_model_json(obj)
            v_instance = v_cls(
                version_operation=operation,
                **data,
            )
            v_old = session.execute(select(v_cls).where(v_cls.id == v_instance.id).order_by(getattr(v_cls, "version_id").desc()).limit(1)).scalar_one_or_none()
            if v_old:
                dump_old = v_old.model_dump(mode="json")
                del(dump_old["version_date_time"])
                del(dump_old["version_id"])
                del(dump_old["version_operation"])
                dump = v_instance.model_dump(mode="json")
                del(dump["version_date_time"])
                del(dump["version_id"])
                del(dump["version_operation"])
                print(dump_old)
                print(dump)
                if dump == dump_old:
                    return
            session.add(v_instance)
    for obj in session.new:
        make_version(obj, versioning.Operation.INSERT)
    for obj in session.dirty:
        make_version(obj, versioning.Operation.UPDATE)
    for obj in session.deleted:
        make_version(obj, versioning.Operation.DELETE)