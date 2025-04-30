import datetime
import re
from typing import Any, Union, Optional
from pydantic import BaseModel
from sqlmodel import SQLModel, Field

def camel_to_snake(s: str) -> str:
    return re.sub(r'([A-Z])([0-9])', r'\1_\2', re.sub(r'([a-z])([A-Z, 0-9])', r'\1_\2', re.sub(r'([0-9])([a-z, A-Z])', r'\1_\2', s))).lower()

class BaseDBModel(SQLModel):
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "__export_exclude_fields__"):
            cls.__export_exclude_fields__: list[str] = []
        cls.__tablename__ = camel_to_snake(cls.__name__)

class BaseDBModelWithId(BaseDBModel):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)

    @property
    def id_strict(self) -> int:
        if isinstance(self.id, int): return self.id
        else: raise DB_ID_NOT_SET_EXCEPTION

class TableDataReturn(BaseModel):
    version: dict[str, Union[int, datetime.datetime]]
    changed: list[dict[str, Any]]
    deleted: list[int]

    def __init__(self, version_id: int, version_date_time: datetime.datetime, changed_objects: list[BaseDBModelWithId], deleted_objects:list[int]):
        self.version = {"version_id": version_id, "version_date_time": version_date_time}
        self.changed = [dump_model_json(obj) for obj in changed_objects]
        self.deleted = deleted_objects

def get_datetime_utc() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)

DB_ID_NOT_SET_EXCEPTION = ValueError("id is not set.")

def db_column_name(c):
    return f"{c.parent.class_.__tablename__}.{c.name}"

def dump_model_json(model: BaseDBModel) -> dict[str, Any]:
    data = model.model_dump(mode="json")
    for remove_field in getattr(model, "__export_exclude_fields__", []):
        del(data[remove_field])
    return data