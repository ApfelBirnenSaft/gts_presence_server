import asyncio
import datetime
import inspect
from sqlalchemy import event, URL
from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from typing import AsyncGenerator
from sqlalchemy.orm import Session as SASession

from utils import  BaseDBModelWithId
from api.database import versioning
from api import models

_database_password = "NV5uqJ96Za8buTyM"
_database_user = "gtsv2_user"
_database_host = "192.168.2.102"
_database_port = 3307
_database = "gtsv2"

database_uri = URL.create("mysql+aiomysql", _database_user, _database_password, _database_host, _database_port, _database, {"charset": "utf8mb4"})

async_engine: AsyncEngine = create_async_engine(database_uri, echo=False, pool_pre_ping=True)

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
    #print("After flush triggered")
    def make_version(obj: BaseDBModelWithId, operation:versioning.Operation):
        obj_cls = type(obj)
        if issubclass(obj_cls, versioning.VersionedDBModel):
            v_cls = obj_cls.version_model()
            data: dict = obj.model_dump(mode="python")
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
                if dump == dump_old:
                    return
            session.add(v_instance)
    for obj in session.new:
        make_version(obj, versioning.Operation.INSERT)
    for obj in session.dirty:
        make_version(obj, versioning.Operation.UPDATE)
    for obj in session.deleted:
        make_version(obj, versioning.Operation.DELETE)

async def create():
    async with async_session() as session:
        await create_all_tables()
        #session.add(models.Activity(activity_type=models.ActivityType.HomeworkRoom, short="235", title="230", room_monday=None, room_tuesday=None, room_wednesday=None, room_thursday=None))
        #session.add(models.Student(first_name="Alexander", last_name="Steinbrück", grade=11, class_id="EK1", monday_homework_room_id=4, tuesday_homework_room_id=4, wednesday_homework_room_id=4, thursday_homework_room_id=4, monday_school_club_id=None, tuesday_school_club_id=None, wednesday_school_club_id=None, thursday_school_club_id=None))
        session.add(models.StudentActivityPresence(issuer_id=1, student_id=3, at_activity_id=4, for_type=models.ActivityType.HomeworkRoom, presence_state=models.PresenceState.Present))
        #(await session.get_one(models.Activity, 1)).title = "241"
        
        await session.commit()

if __name__ == "__main__":
    asyncio.run(create())