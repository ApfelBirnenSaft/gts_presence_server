import datetime as DateTime
from enum import Enum
from typing import Optional

from . import db

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key = True, nullable=False)
    last_change = db.Column(db.DateTime, nullable=False)
    
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    class_id = db.Column(db.Text, nullable=False)

    monday_homework_room_id = db.Column(db.Integer, nullable=True)
    tuesday_homework_room_id = db.Column(db.Integer, nullable=True)
    wednesday_homework_room_id = db.Column(db.Integer, nullable=True)
    thursday_homework_room_id = db.Column(db.Integer, nullable=True)

    monday_school_club_id = db.Column(db.Integer, nullable=True)
    tuesday_school_club_id = db.Column(db.Integer, nullable=True)
    wednesday_school_club_id = db.Column(db.Integer, nullable=True)
    thursday_school_club_id = db.Column(db.Integer, nullable=True)

    def __init__(self, first_name:str, last_name:str, grade:int, class_id:str,
                 monday_homework_room_id:int, tuesday_homework_room_id:int, wednesday_homework_room_id:int, thursday_homework_room_id:int,
                 monday_school_club_id:int, tuesday_school_club_id:int, wednesday_school_club_id:int, thursday_school_club_id:int):
        self.first_name = first_name
        self.last_name = last_name
        self.grade = grade
        self.class_id = class_id

        self.monday_homework_room_id = monday_homework_room_id
        self.tuesday_homework_room_id = tuesday_homework_room_id
        self.wednesday_homework_room_id = wednesday_homework_room_id
        self.thursday_homework_room_id = thursday_homework_room_id

        self.monday_school_club_id = monday_school_club_id
        self.tuesday_school_club_id = tuesday_school_club_id
        self.wednesday_school_club_id = wednesday_school_club_id
        self.thursday_school_club_id = thursday_school_club_id

        self.last_change = DateTime.datetime.now()

    def __repr__(self):
        return f'<Student {self.id} {self.first_name} {self.last_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'grade': self.grade,
            'class_id': self.class_id,
            'monday_homework_room_id': self.monday_homework_room_id,
            'tuesday_homework_room_id': self.tuesday_homework_room_id,
            'wednesday_homework_room_id': self.wednesday_homework_room_id,
            'thursday_homework_room_id': self.thursday_homework_room_id,
            'monday_school_club_id': self.monday_school_club_id,
            'tuesday_school_club_id': self.tuesday_school_club_id,
            'wednesday_school_club_id': self.wednesday_school_club_id,
            'thursday_school_club_id': self.thursday_school_club_id,
        }



class StudentNote(db.Model):
    __tablename__ = "student_notes"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    datetime = db.Column(db.DateTime, nullable=False)
    issuer_id = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, nullable=False)
    note = db.Column(db.Text, nullable=False)

    def __init__(self, issuer_id:int, student_id:int, note:str):
        self.issuer_id = issuer_id
        self.student_id = student_id
        self.note = note

        self.datetime = DateTime.datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'datetime': self.datetime,
            'issuer_id': self.issuer_id,
            'student_id': self.student_id,
            'note': self.note,
        }



class StudentAbsentIrregular(db.Model):
    __tablename__ = 'student_absence_irregular'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_id = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, nullable=False)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by_id = db.Column(db.Integer, nullable=True)


    def __init__(self, created_at: DateTime.datetime, created_by_id: int, student_id: int, start_datetime: DateTime.datetime, end_datetime: DateTime.datetime, deleted_at: Optional[DateTime.datetime] = None, deleted_by_id: Optional[int] = None):
        self.created_by_id = created_by_id
        self.student_id = student_id
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime

        self.deleted_at = deleted_at
        self.deleted_by_id = deleted_by_id

        self.created_at = created_at

    def __repr__(self):
        return f'<StudentAbsentIrregular {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'created_by_id': self.created_by_id,
            'student_id': self.student_id,
            'start_datetime': self.start_datetime.isoformat(),
            'end_datetime': self.end_datetime.isoformat(),
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at != None else None,
            'deleted_by_id': self.deleted_by_id,
        }



class StudentAbsentRegular(db.Model):
    __tablename__ = 'student_absence_regular'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by_id = db.Column(db.Integer, nullable=True)

    valid_from = db.Column(db.Date, nullable=False)
    valid_until = db.Column(db.Date, nullable=True)

    student_id = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    monday = db.Column(db.Boolean, nullable=False)
    tuesday = db.Column(db.Boolean, nullable=False)
    wednesday = db.Column(db.Boolean, nullable=False)
    thursday = db.Column(db.Boolean, nullable=False)
    
    deleted_at = db.Column(db.DateTime, nullable=True)
    deleted_by_id = db.Column(db.Integer, nullable=True)

    
    def __init__(
        self, 
        valid_from: DateTime.date, 
        valid_until: Optional[DateTime.date], 
        student_id: int, 
        start_time: DateTime.time, 
        end_time: DateTime.time, 
        monday: bool, 
        tuesday: bool, 
        wednesday: bool, 
        thursday: bool, 
        created_at: DateTime.datetime, 
        created_by_id: Optional[int] = None, 
        deleted_at: Optional[DateTime.datetime] = None, 
        deleted_by_id: Optional[int] = None
    ):
        self.created_at = created_at
        self.created_by_id = created_by_id
        self.valid_from = valid_from
        self.valid_until = valid_until
        self.student_id = student_id
        self.start_time = start_time
        self.end_time = end_time
        self.monday = monday
        self.tuesday = tuesday
        self.wednesday = wednesday
        self.thursday = thursday
        self.deleted_at = deleted_at
        self.deleted_by_id = deleted_by_id

    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'created_by_id': self.created_by_id,
            'valid_from': self.valid_from.isoformat(),
            'valid_until': self.valid_until.isoformat() if self.valid_until != None else None,
            'student_id': self.student_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'monday': self.monday,
            'tuesday': self.tuesday,
            'wednesday': self.wednesday,
            'thursday': self.thursday,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at != None else None,
            'deleted_by_id': self.deleted_by_id
        }



class PresenceState(Enum):
    Present = "present"
    Absent = "absent"
    Missing = "missing"

    def from_string(string):
        return {
            PresenceState.Present.value: PresenceState.Present,
            PresenceState.Absent.value: PresenceState.Absent,
            PresenceState.Missing.value: PresenceState.Missing,
            }[string]

    def __str__(self):
        return self.value

class StudentHomeworkRoomPresence(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    datetime = db.Column(db.DateTime, nullable=False)
    issuer_id = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, nullable=False)
    from_activity_string_id = db.Column(db.Text, nullable=True)
    presence_state = db.Column(db.Enum(PresenceState), nullable=False)

    def __init__(self, issuer_id:int, student_id:int, presence_state:PresenceState, from_activity_string_id:str, datetime:Optional[DateTime.datetime] = None):
        self.issuer_id = issuer_id
        self.student_id = student_id
        self.presence_state = presence_state
        self.from_activity_string_id = from_activity_string_id
        if isinstance(datetime, DateTime.datetime):
            self.datetime = datetime
        else:
            self.datetime = datetime.datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'datetime': self.datetime.isoformat(),
            'issuer_id': self.issuer_id,
            'student_id': self.student_id,
            'presence_state': str(self.presence_state),
            'from_activity_string_id': self.from_activity_string_id,
        }

class StudentSchoolClubPresence(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    datetime = db.Column(db.DateTime, nullable=False)
    issuer_id = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, nullable=False)
    from_activity_string_id = db.Column(db.Text, nullable=True)
    presence_state = db.Column(db.Enum(PresenceState), nullable=False)

    def __init__(self, issuer_id:int, student_id:int, presence_state:PresenceState, from_activity_string_id:str, datetime:Optional[DateTime.datetime] = None):
        self.issuer_id = issuer_id
        self.student_id = student_id
        self.presence_state = presence_state
        self.from_activity_string_id = from_activity_string_id
        if isinstance(datetime, DateTime.datetime):
            self.datetime = datetime
        else:
            self.datetime = datetime.datetime.now()

    def to_dict(self):
        return {
            'id': self.id,
            'datetime': self.datetime.isoformat(),
            'issuer_id': self.issuer_id,
            'student_id': self.student_id,
            'presence_state': str(self.presence_state),
            'from_activity_string_id': self.from_activity_string_id,
        }
