from copy import copy
from sqlmodel import Field, func, select
from typing import Optional, Type
import datetime
import enum
from pydantic import create_model
from sqlalchemy.ext.asyncio import AsyncSession

from utils import get_datetime_utc, camel_to_snake, DB_ID_NOT_SET_EXCEPTION, dump_model_json

from .base_model import DBModel

class Operation(enum.Enum):
    UPDATE = "update"
    DELETE = "delete"
    INSERT = "insert"

class VersionDBModel(DBModel):
    version_id: Optional[int] = Field(primary_key=True, nullable=False, default=None)
    version_operation: Operation
    version_date_time: datetime.datetime = Field(default_factory=get_datetime_utc)

    @property
    def version_id_strict(self) -> int:
        if isinstance(self.version_id, int): return self.version_id
        else: raise DB_ID_NOT_SET_EXCEPTION

class VersionedDBModel(DBModel):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "__version_exclude_fields__"):
            cls.__version_exclude_fields__: list[str] = []
    
    @classmethod
    def identifier_column(cls) -> str:
        try:
            return getattr(cls, "__identifier_column__")
        except AttributeError:
            raise AttributeError(f"Class {cls.__name__} does not have an '__identifier_column__' attribute.")
    
    @classmethod
    def version_model(cls) -> Type[VersionDBModel]:
        if getattr(cls, "__version_model__", None) == None:
            raise ValueError("VersionedDBModel seems not to be initialized")
        return cls.__version_model__
    
    @classmethod
    def init_version_model(cls):
        cls.__version_model__ = create_version_model(cls)
    
    @classmethod
    async def get_changes(cls, session: AsyncSession, last_version_id: int, only_till: Optional[datetime.datetime]):
        data = {}
        versioning_cls = cls.version_model()
        highest_version = (await session.execute(select(versioning_cls).order_by(getattr(versioning_cls.version_id, 'desc')()).limit(1))).scalar_one_or_none()
        if highest_version == None or highest_version.version_id_strict <= last_version_id:
            data.setdefault("version", {})["id"] = highest_version.version_id_strict if highest_version != None else 0
            data["version"]["date_time"] = highest_version.version_date_time.isoformat() if highest_version != None else None
            data.setdefault("deleted", [])
            data.setdefault("changed", [])
            return data
        subquery = (select(
                getattr(versioning_cls, cls.identifier_column()),
                func.max(versioning_cls.version_id).label("max_id")
            )
            .where(getattr(versioning_cls.version_id, "version_id") > last_version_id)
            .group_by(getattr(versioning_cls, cls.identifier_column()))
            .order_by(getattr(versioning_cls, "version_id"))
            .subquery()
        )
        query = (
            select(versioning_cls)
            .join(subquery, versioning_cls.version_id == getattr(subquery.c, "max_id"))
        )
        versions = (await session.execute(query)).scalars()
        for version in versions:
            identifier = getattr(version, cls.identifier_column())
            data.setdefault("version", {})["id"] = version.version_id_strict
            data["version"]["date_time"] = version.version_date_time.isoformat()
            if version.version_operation == Operation.DELETE:
                data.setdefault("deleted", []).append(identifier)
            else:
                data.setdefault("changed", []).append(dump_model_json((await session.get_one(cls, identifier))))
        return data

def create_version_model(model_cls: Type[VersionedDBModel]) -> Type[VersionDBModel]:
    fields = {}
    for name, field in model_cls.model_fields.items():
        if name in model_cls.__version_exclude_fields__:
            continue
        field = copy(field)
        field.unique = False
        field.foreign_key = []
        if field.primary_key and field.annotation is Optional[int]:
            field.annotation = int
            field.primary_key = False
        fields[name] = (field.annotation, field)

    version_cls_name = f"{model_cls.__name__}Version"
    table_name = camel_to_snake(version_cls_name)
    version_cls = create_model(
        version_cls_name,
        __base__=VersionDBModel,
        __cls_kwargs__={"table": True},
        __tablename__=table_name,
        **fields
    )
    return version_cls