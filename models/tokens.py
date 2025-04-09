from enum import Enum
from . import db
import datetime as DateTime

class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"

class Token(db.Model):
    __tablename__ = 'tokens'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255), nullable=False, unique=True)
    user_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    token_type = db.Column(db.Enum(TokenType), nullable=False)

    def __repr__(self):
        return f"<Token id={self.id} token={self.token} expires_at={self.expires_at}>"

    def has_expired(self):
        """Prüfen, ob das Token abgelaufen ist."""
        return DateTime.datetime.now() > self.expires_at