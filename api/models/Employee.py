from sqlmodel import SQLModel, Field, BINARY
from typing import Optional
import datetime

class Employee(SQLModel, table=True):
    #id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    username: str = Field(nullable=False, primary_key=True, max_length=64)
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    title: Optional[str] = Field(nullable=True)
    salutation: str = Field(nullable=False)

    salt: str = Field(max_length=32, nullable=False)
    verifier: str = Field(max_length=512, nullable=False)
    sec_lvl: int = Field(nullable=False)

    """
    @property
    def id_strict(self) -> int:
        if isinstance(self.id, int): return self.id
        else: raise ValueError("id is not set.")"""

"""
class EmployeeAudit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    employee_id: int = Field(nullable=False, foreign_key="employee.id", index=True)
    username: str = Field(nullable=False)
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    title: Optional[str] = Field(nullable=True)
    salutation: str = Field(nullable=False)

    @property
    def id_strict(self) -> int:
        if isinstance(self.id, int): return self.id
        else: raise ValueError("id is not set.")"""