from sqlmodel import Field
from typing import Optional

from api.database import VersionedDBModel
from .activity import Activity
from utils import db_column_name

class Employee(VersionedDBModel, table=True):
    username: str = Field(nullable=False, unique=True, max_length=64)
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    title: Optional[str] = Field(nullable=True)
    salutation: str = Field(nullable=False)

    salt: str = Field(max_length=32, nullable=False, exclude=True)
    verifier: str = Field(max_length=512, nullable=False, exclude=True)
    sec_lvl: int = Field(nullable=False)

    monday_homework_room_id: Optional[int] = Field(nullable=True, foreign_key=db_column_name(Activity.id))
    tuesday_homework_room_id: Optional[int] = Field(nullable=True, foreign_key=db_column_name(Activity.id))
    wednesday_homework_room_id: Optional[int] = Field(nullable=True, foreign_key=db_column_name(Activity.id))
    thursday_homework_room_id: Optional[int] = Field(nullable=True, foreign_key=db_column_name(Activity.id))

    monday_school_club_id: Optional[int] = Field(nullable=True, foreign_key=db_column_name(Activity.id))
    tuesday_school_club_id: Optional[int] = Field(nullable=True, foreign_key=db_column_name(Activity.id))
    wednesday_school_club_id: Optional[int] = Field(nullable=True, foreign_key=db_column_name(Activity.id))
    thursday_school_club_id: Optional[int] = Field(nullable=True, foreign_key=db_column_name(Activity.id))
