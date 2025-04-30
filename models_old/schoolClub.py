from typing import Optional
import datetime as DateTime

from . import db

class SchoolClub(db.Model):
    __tablename__ = 'school_clubs'

    id = db.Column(db.Integer, primary_key = True, nullable=False)
    last_change = db.Column(db.DateTime, nullable=False)
    
    short = db.Column(db.Text, nullable=False, unique=True)
    title = db.Column(db.Text, nullable=False)
    
    room_monday = db.Column(db.Text, nullable=True)
    room_tuesday = db.Column(db.Text, nullable=True)
    room_wednesday = db.Column(db.Text, nullable=True)
    room_thursday = db.Column(db.Text, nullable=True)

    def __init__(self, short:str, title:str, room_monday:Optional[str] = None, room_tuesday:Optional[str] = None, room_wednesday:Optional[str] = None, room_thursday:Optional[str] = None):
        self.short = short
        self.title = title

        self.room_monday = room_monday
        self.room_tuesday = room_tuesday
        self.room_wednesday = room_wednesday
        self.room_thursday = room_thursday
        self.last_change = DateTime.datetime.now()

    def __repr__(self):
        return f'<SchoolClub {self.id} {self.short} {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'short': self.short,
            'title': self.title,

            'room_monday': self.room_monday,
            'room_tuesday': self.room_tuesday,
            'room_wednesday': self.room_wednesday,
            'room_thursday': self.room_thursday,
        }