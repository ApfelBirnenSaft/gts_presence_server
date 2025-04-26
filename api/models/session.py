from sqlmodel import SQLModel, Field

from .__init__ import db_column_name, Employee
        
class AuthSession(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    challange: str
    key: str
    user_id: int = Field(nullable=False, foreign_key=db_column_name(Employee.id))
