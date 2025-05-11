import datetime
import hashlib
import hmac
import re
import secrets
from typing import Any, Literal, Union, Optional
from pydantic import BaseModel
from sqlmodel import SQLModel, Field

DB_ID_NOT_SET_EXCEPTION = ValueError("id is not set.")

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
        self.changed = [obj.model_dump(mode="json") for obj in changed_objects]
        self.deleted = deleted_objects

def get_datetime_utc() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)

def db_column_name(c):
    return f"{c.parent.class_.__tablename__}.{c.name}"

def calc_hmac(data: bytes, key: bytes) -> str:
    h = hmac.new(key, data, hashlib.sha256)
    return h.hexdigest()

def verify_hmac(calculated_hmac:Union[str, bytes], expected_hmac: Union[str, bytes]) -> bool:
    return hmac.compare_digest(
        calculated_hmac.encode() if isinstance(calculated_hmac, str) else calculated_hmac,
        expected_hmac.encode() if isinstance(expected_hmac, str) else expected_hmac
    )

def generate_challenge(length: int = 16) -> str:
    return secrets.token_hex(length)