from sqlmodel import SQLModel, Field
from typing import Optional
import datetime, enum

from .__init__ import db_column_name, Activity, Employee

from api.database import versioning

from utils import DB_ID_NOT_SET_EXCEPTION

class Student(SQLModel, versioning.VersionedMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    last_change: datetime.datetime = Field(nullable=False)
    
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    grade: int = Field(nullable=False)
    class_id: str = Field(nullable=False)

    monday_homework_room_id: Optional[int] = Field(nullable=True, foreign_key=db_column_name(Activity.id))
    tuesday_homework_room_id: Optional[int] = Field(nullable=True, foreign_key=db_column_name(Activity.id))
    wednesday_homework_room_id: Optional[int] = Field(nullable=True, foreign_key=db_column_name(Activity.id))
    thursday_homework_room_id: Optional[int] = Field(nullable=True, foreign_key=db_column_name(Activity.id))

    monday_school_club_id: Optional[int] = Field(nullable=True, foreign_key=db_column_name(Activity.id))
    tuesday_school_club_id: Optional[int] = Field(nullable=True, foreign_key=db_column_name(Activity.id))
    wednesday_school_club_id: Optional[int] = Field(nullable=True, foreign_key=db_column_name(Activity.id))
    thursday_school_club_id: Optional[int] = Field(nullable=True, foreign_key=db_column_name(Activity.id))

    @property
    def id_strict(self) -> int:
        if isinstance(self.id, int): return self.id
        else: raise DB_ID_NOT_SET_EXCEPTION


class StudentNote(SQLModel, versioning.VersionedMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    date_time: datetime.datetime = Field(nullable=False)
    issuer_id: int = Field(nullable=False, foreign_key=db_column_name(Employee.id))
    student_id: int = Field(nullable=False, foreign_key=db_column_name(Student.id))
    note: str = Field(nullable=False)

    @property
    def id_strict(self) -> int:
        if isinstance(self.id, int): return self.id
        else: raise DB_ID_NOT_SET_EXCEPTION

class StudentAbsentIrregular(SQLModel, versioning.VersionedMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    created_at: datetime.datetime = Field(nullable=False)
    created_by_id: int = Field(nullable=False, foreign_key=db_column_name(Employee.id))
    student_id: int = Field(nullable=False, foreign_key=db_column_name(Student.id))
    start_datetime: datetime.datetime = Field(nullable=False)
    end_datetime: datetime.datetime = Field(nullable=False)

    @property
    def id_strict(self) -> int:
        if isinstance(self.id, int): return self.id
        else: raise DB_ID_NOT_SET_EXCEPTION

class StudentAbsentRegular(SQLModel, versioning.VersionedMixin, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    created_at: datetime.datetime = Field(nullable=False)
    created_by_id: Optional[int] = Field(nullable=True, foreign_key=db_column_name(Employee.id))

    valid_from: datetime.date = Field(nullable=False)
    valid_until: Optional[datetime.date] = Field(nullable=True)

    student_id: int = Field(nullable=False, foreign_key=db_column_name(Student.id))
    start_time: datetime.time = Field(nullable=False)
    end_time: datetime.time = Field(nullable=False)
    monday: bool = Field(nullable=False)
    tuesday: bool = Field(nullable=False)
    wednesday: bool = Field(nullable=False)
    thursday: bool = Field(nullable=False)

    @property
    def id_strict(self) -> int:
        if isinstance(self.id, int): return self.id
        else: raise DB_ID_NOT_SET_EXCEPTION

class PresenceState(enum.Enum):
    Present = "present"
    Absent = "absent"
    Missing = "missing"

    @staticmethod
    def from_string(string):
        return {
            PresenceState.Present.value: PresenceState.Present,
            PresenceState.Absent.value: PresenceState.Absent,
            PresenceState.Missing.value: PresenceState.Missing,
            }[string]

    def __str__(self):
        return self.value

class StudentActivityPresence(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    date_time: datetime.datetime = Field(nullable=False)
    issuer_id: int = Field(nullable=False, foreign_key=db_column_name(Employee.id))
    student_id: int = Field(nullable=False, foreign_key=db_column_name(Student.id))
    from_activity_id: Optional[int] = Field(nullable=True, foreign_key=db_column_name(Activity.id))
    presence_state: PresenceState = Field(nullable=False)

    @property
    def id_strict(self) -> int:
        if isinstance(self.id, int): return self.id
        else: raise DB_ID_NOT_SET_EXCEPTION

class StudentHomeworkExtension(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    date_time: datetime.datetime = Field(nullable=False)
    issuer_id: int = Field(nullable=False, foreign_key=db_column_name(Employee.id))
    student_id: int = Field(nullable=False, foreign_key=db_column_name(Student.id))
    from_activity_id: Optional[int] = Field(nullable=True, foreign_key=db_column_name(Activity.id))
    extension: bool = Field(nullable=False)

    @property
    def id_strict(self) -> int:
        if isinstance(self.id, int): return self.id
        else: raise DB_ID_NOT_SET_EXCEPTION
