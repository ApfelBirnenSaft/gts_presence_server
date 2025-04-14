from sqlmodel import SQLModel, Field
from typing import Optional
import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    created: datetime.datetime
