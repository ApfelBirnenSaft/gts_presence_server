from .audit import *
import datetime as DateTime

class HomeworkRoomAudit(db.Model):
    __tablename__ = 'homework_rooms' + '_audit'

    audit_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    audit_action = db.Column(db.Enum(AuditAction), nullable=False)
    audit_datetime = db.Column(db.DateTime, nullable=False)
    audit_issuer_id = db.Column(db.Integer, nullable=True)

    id = db.Column(db.Integer, nullable=False)#, primary_key = True, nullable=False)
    last_change = db.Column(db.DateTime, nullable=False)
    
    room = db.Column(db.Text, nullable=False)

    def __init__(self, audit_id:int, audit_action:AuditAction, audit_datetime: DateTime, audit_issuer_id:Optional["int"], room:str):
        self.audit_id = audit_id
        self.audit_action = audit_action
        self.audit_datetime = audit_datetime
        self.audit_issuer_id = audit_issuer_id
        
        self.room = room
        self.last_change = DateTime.datetime.now()

    def __repr__(self):
        return f'<HomeworkRoom {self.id} {self.room}>'

    def to_dict(self):
        return {
            'audit_id': self.audit_id,
            'audit_action': self.audit_action,
            'audit_datetime': self.audit_datetime,
            'audit_issuer_id': self.audit_issuer_id,

            'id': self.id,
            'room': self.room
        }