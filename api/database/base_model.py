from sqlmodel import SQLModel

class DBModel(SQLModel):
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.__export_exclude_fields__ = []