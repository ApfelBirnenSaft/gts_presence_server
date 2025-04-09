from . import db
import datetime as DateTime

class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key = True, nullable=False)
    last_change = db.Column(db.DateTime, nullable=False)

    prefix = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    short_name = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    sec_lvl = db.Column(db.Integer, nullable=False)
    password_change_recomended = db.Column(db.Boolean, nullable=False)

    monday_homework_room_id = db.Column(db.Integer, nullable=True)
    tuesday_homework_room_id = db.Column(db.Integer, nullable=True)
    wednesday_homework_room_id = db.Column(db.Integer, nullable=True)
    thursday_homework_room_id = db.Column(db.Integer, nullable=True)

    monday_school_club_id = db.Column(db.Integer, nullable=True)
    tuesday_school_club_id = db.Column(db.Integer, nullable=True)
    wednesday_school_club_id = db.Column(db.Integer, nullable=True)
    thursday_school_club_id = db.Column(db.Integer, nullable=True)

    def __init__(self, prefix:str, first_name:str, last_name:str, short_name:str, password:str, sec_lvl:int, password_change_recomended: bool,
                 monday_homework_room_id:int, tuesday_homework_room_id:int, wednesday_homework_room_id:int, thursday_homework_room_id:int,
                 monday_school_club_id:int, tuesday_school_club_id:int, wednesday_school_club_id:int, thursday_school_club_id:int):
        
        self.prefix = prefix
        self.first_name = first_name
        self.last_name = last_name
        self.short_name = short_name
        self.password = password
        self.sec_lvl = sec_lvl
        self.password_change_recomended = password_change_recomended

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
        return f'<Employee {self.id} {self.first_name} {self.last_name}>'

    def to_dict(self, password_change_recomended_null:True = True):
        return {
            'id': self.id,
            'prefix': self.prefix,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'short_name': self.short_name,
            'sec_lvl': self.sec_lvl,
            'password_change_recomended': None if password_change_recomended_null else self.password_change_recomended,

            'monday_homework_room_id': self.monday_homework_room_id,
            'tuesday_homework_room_id': self.tuesday_homework_room_id,
            'wednesday_homework_room_id': self.wednesday_homework_room_id,
            'thursday_homework_room_id': self.thursday_homework_room_id,
            
            'monday_school_club_id': self.monday_school_club_id,
            'tuesday_school_club_id': self.tuesday_school_club_id,
            'wednesday_school_club_id': self.wednesday_school_club_id,
            'thursday_school_club_id': self.thursday_school_club_id,
        }