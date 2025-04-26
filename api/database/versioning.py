from copy import copy, deepcopy
import inspect
import json
from sqlmodel import SQLModel, Field, Enum
from typing import Optional, Type
import datetime
import enum
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncEngine
from pydantic import create_model

from utils import get_datetime_utc, camel_to_snake

from utils import DB_ID_NOT_SET_EXCEPTION

VERSION_CLASS = "version_class"

class Operation(enum.Enum):
    UPDATE = "update"
    DELETE = "delete"
    INSERT = "insert"


class VersionModelMixin(SQLModel):
    version_id: Optional[int] = Field(primary_key=True, nullable=False, default=None)
    version_operation: Operation
    version_date_time: datetime.datetime = Field(default_factory=get_datetime_utc)

    @property
    def version_id_strict(self) -> int:
        if isinstance(self.version_id, int): return self.version_id
        else: raise DB_ID_NOT_SET_EXCEPTION

class VersionedMixin:
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.__versioned__ = {}

    @classmethod
    def get_version_class(cls) -> Type[VersionModelMixin]:
        return cls.__versioned__[VERSION_CLASS]

def create_version_model(model_cls: Type[VersionedMixin]) -> Type[VersionModelMixin]:
    if not issubclass(model_cls, VersionedMixin):
        raise ValueError("to create version model, the model needs to have the VersionedMixin")
    
    exclude_fields = getattr(model_cls, "__version_exclude_fields__", [])

    fields = {}

    for name, anno in model_cls.__annotations__.items():
        if name in exclude_fields:
            continue
        field = copy(getattr(model_cls, name, None))
        if isinstance(field, sqlalchemy.orm.attributes.InstrumentedAttribute):
            column = getattr(field, "property").columns[0]
            if column.primary_key:
                if anno is Optional[int]:
                    fields[name] = (int, field)
                    continue
            fields[name] = (anno, field)

    version_cls_name = f"{model_cls.__name__}Version"
    table_name = camel_to_snake(version_cls_name)
    version_cls = create_model(
        version_cls_name,
        __base__=VersionModelMixin,
        __cls_kwargs__={"table": True},
        __tablename__=table_name,
        **fields
    )
    model_cls.__versioned__[VERSION_CLASS] = version_cls
    return version_cls

def create_all_version_models(models_module: object):
    bla = []
    for name, obj in inspect.getmembers(models_module):
        if inspect.isclass(obj):
            if issubclass(obj, SQLModel) and issubclass(obj, VersionedMixin):
                #print(f"version model of {obj.__name__} " + "-"*80)
                #for b in bla:
                #    print(b.get_version_class().__name__)
                create_version_model(obj)
                #bla.append(obj)
    #v: Type[VersionModelMixin] = bla[0].get_version_class()
    #print(json.dumps(v.model_json_schema(), indent=4))

def make_versioned(models_module: object, engine: AsyncEngine):
    create_all_version_models(models_module)