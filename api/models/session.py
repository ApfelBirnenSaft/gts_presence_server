from sqlmodel import Field

from api.database import DBModel
from .employee import Employee
from utils import db_column_name
        
class AuthSession(DBModel, table=True):
    id: str = Field(default=None, primary_key=True)
    challange: str
    key: str
    user_id: int = Field(nullable=False, foreign_key=db_column_name(Employee.id))
