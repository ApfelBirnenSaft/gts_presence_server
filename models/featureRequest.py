from . import db
from enum import Enum
from typing import Optional
import datetime as DateTime

class RequestStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    REJECTED = "rejected"

class FeatureRequest(db.Model):
    __tablename__ = 'feature_requests'

    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime, nullable=False)
    last_change = db.Column(db.DateTime, nullable=False)
    
    issuer_id = db.Column(db.Integer, nullable=False)
    removed_at = db.Column(db.DateTime, nullable=True)
    removed_by_id = db.Column(db.Integer, nullable=True)
    title = db.Column(db.Text, nullable=True)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(RequestStatus), default=RequestStatus.OPEN, nullable=False)
    is_comment = db.Column(db.Boolean, default=False, nullable=False)
    
    parent_id = db.Column(db.Integer, db.ForeignKey('feature_requests.id'), nullable=True)

    def __init__(self, datetime:DateTime.datetime, issuer_id:int, message:str, title:Optional[str] = None, removed_at:Optional[DateTime.datetime] = None, removed_by_id:Optional[int] = None, status:RequestStatus = RequestStatus.OPEN, is_comment:bool = False, parent_id:Optional[int] = None):
        self.datetime = datetime
        self.last_change = datetime
        self.issuer_id = issuer_id
        self.removed_at = removed_at
        self.removed_by_id = removed_by_id
        self.title = title
        self.message = message
        self.status = status
        self.is_comment = is_comment
        self.parent_id = parent_id

    def to_dict(self):
        return {
            'id': self.id,
            'datetime': self.datetime.isoformat(),
            'last_change': self.last_change.isoformat(),
            'issuer_id': self.issuer_id,
            'removed_at': self.removed_at,
            'removed_by_id': self.removed_by_id,
            'message': self.message,
            'title': self.title,
            'status': self.status.name,
            'is_comment': self.is_comment,
            'parent_id': self.parent_id,
        }

    def __repr__(self):
        return f'<FeatureRequest {self.id}, Status {self.status}>'