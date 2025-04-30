from . import db
import datetime as DateTime

class HomeworkRoom(db.Model):
    __tablename__ = 'homework_rooms'

    id = db.Column(db.Integer, primary_key = True, nullable=False)
    last_change = db.Column(db.DateTime, nullable=False)
    
    room = db.Column(db.Text, nullable=False)

    def __init__(self, room:str):
        self.room = room
        self.last_change = DateTime.datetime.now()

    def __repr__(self):
        return f'<HomeworkRoom {self.id} {self.room}>'

    def to_dict(self):
        return {
            'id': self.id,
            'room': self.room
        }