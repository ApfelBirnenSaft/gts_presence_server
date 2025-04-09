from typing import Optional
import datetime as DateTime

from .audit import *

class SchoolClubAudit(db.Model):
    __tablename__ = 'school_clubs' + '_audit'

    audit_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    audit_action = db.Column(db.Enum(AuditAction), nullable=False)
    audit_datetime = db.Column(db.DateTime, nullable=False)
    audit_issuer_id = db.Column(db.Integer, nullable=True)

    id = db.Column(db.Integer, nullable=False)#, primary_key = True, nullable=False)
    last_change = db.Column(db.DateTime, nullable=False)
    
    short = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text, nullable=False)
    
    room_monday = db.Column(db.Text, nullable=True)
    room_tuesday = db.Column(db.Text, nullable=True)
    room_wednesday = db.Column(db.Text, nullable=True)
    room_thursday = db.Column(db.Text, nullable=True)

    def __init__(self, audit_id:int, audit_action:AuditAction, audit_datetime: DateTime, audit_issuer_id:Optional["int"], short:str, title:str, room_monday:Optional[str] = None, room_tuesday:Optional[str] = None, room_wednesday:Optional[str] = None, room_thursday:Optional[str] = None):
        self.audit_id = audit_id
        self.audit_action = audit_action
        self.audit_datetime = audit_datetime
        self.audit_issuer_id = audit_issuer_id
        
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
            'audit_id': self.audit_id,
            'audit_action': self.audit_action,
            'audit_datetime': self.audit_datetime,
            'audit_issuer_id': self.audit_issuer_id,

            'id': self.id,
            'short': self.short,
            'title': self.title,

            'room_monday': self.room_monday,
            'room_tuesday': self.room_tuesday,
            'room_wednesday': self.room_wednesday,
            'room_thursday': self.room_thursday,
        }