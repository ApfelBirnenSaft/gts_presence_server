from typing import Optional
from sqlmodel import SQLModel, Field
        
class AuthSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    challange: str
    key: str = Field(unique=True)
    username: str

    @property
    def id_strict(self) -> int:
        if isinstance(self.id, int): return self.id
        else: raise ValueError("id is not set.")