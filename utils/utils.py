import datetime
import re
from sqlmodel import SQLModel

class DBModel(SQLModel):
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.__export_exclude_fields__ = []
        cls.__tablename__ = camel_to_snake(cls.__name__)

def get_datetime_utc() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)

def camel_to_snake(s: str) -> str:
    result = re.sub(r'([A-Z])', r'_\1', s).lower()
    for c in s:
        if c != "_":
            if re.match(r'([A-Z])', c):
                result = result[1:]
            break
    return result

DB_ID_NOT_SET_EXCEPTION = ValueError("id is not set.")

def db_column_name(c):
    return f"{c.parent.class_.__tablename__}.{c.name}"

def dump_model_json(model: DBModel) -> dict:
    data = model.model_dump(mode="json")
    for remove_field in getattr(model, "__export_exclude_fields__", []):
        del(data[remove_field])
    return data