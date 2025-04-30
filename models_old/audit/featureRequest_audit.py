from .audit import *
from ..featureRequest import *
from typing import Optional
import datetime as DateTime

class FeatureRequestAudit(db.Model):
    __tablename__ = 'feature_requests' + '_audit'

    audit_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    audit_action = db.Column(db.Enum(AuditAction), nullable=False)
    audit_datetime = db.Column(db.DateTime, nullable=False)
    audit_issuer_id = db.Column(db.Integer, nullable=True)

    id = db.Column(db.Integer, nullable=False)#, primary_key = True, nullable=False)
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

    def __init__(self, audit_id:int, audit_action:AuditAction, audit_datetime: DateTime, audit_issuer_id:Optional["int"], datetime:DateTime.datetime, issuer_id:int, message:str, title:Optional[str] = None, removed_at:Optional[DateTime.datetime] = None, removed_by_id:Optional[int] = None, status:RequestStatus = RequestStatus.OPEN, is_comment:bool = False, parent_id:Optional[int] = None):
        self.audit_id = audit_id
        self.audit_action = audit_action
        self.audit_datetime = audit_datetime
        self.audit_issuer_id = audit_issuer_id
        
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
            'audit_id': self.audit_id,
            'audit_action': self.audit_action,
            'audit_datetime': self.audit_datetime,
            'audit_issuer_id': self.audit_issuer_id,

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