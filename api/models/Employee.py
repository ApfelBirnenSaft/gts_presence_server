from sqlmodel import Field
from typing import Optional

from api.database import VersionedDBModel

from utils import DB_ID_NOT_SET_EXCEPTION

class Employee(VersionedDBModel, table=True):
    __identifier_column__ = "id"
    __version_exclude_fields__ = ["salt", "verifier"]
    __export_exclude_fields__ = ["salt", "verifier"]

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    username: str = Field(nullable=False, unique=True, max_length=64)
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    title: Optional[str] = Field(nullable=True)
    salutation: str = Field(nullable=False)

    salt: str = Field(max_length=32, nullable=False)
    verifier: str = Field(max_length=512, nullable=False)
    sec_lvl: int = Field(nullable=False)

    @property
    def id_strict(self) -> int:
        if isinstance(self.id, int): return self.id
        else: raise DB_ID_NOT_SET_EXCEPTION
