from sqlmodel import Relationship, SQLModel, Field
from typing import Optional
import datetime

from api.models import Employee

class DataChange(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)

    employee_username: Optional[int] = Field(default=None, foreign_key=Employee.username)

    employee: Optional[Employee] = Relationship()

    @property
    def id_strict(self) -> int:
        if isinstance(self.id, int): return self.id
        else: raise ValueError("id is not set.")