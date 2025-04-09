class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key = True, nullable=False)
    prefix = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    short_name = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    sec_lvl = db.Column(db.Integer, nullable=False)

    def __init__(self, prefix:str, first_name:str, last_name:str, short_name:str, password:str, sec_lvl:int):
        self.prefix = prefix
        self.first_name = first_name
        self.last_name = last_name
        self.short_name = short_name
        self.password = password
        self.sec_lvl = sec_lvl

    def __repr__(self):
        return f'<Employee {self.id} {self.first_name} {self.last_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'prefix': self.prefix,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'short_name': self.short_name,
            'sec_lvl': self.sec_lvl
        }



class EmployeeHomeworkRoom(db.Model):
    __tablename__ = 'employee_homework_room'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(datetime.UTC))
    issuer_id = db.Column(db.Integer, nullable=False)
    employee_id = db.Column(db.Integer, nullable=False)
    monday = db.Column(db.Text, nullable=True)
    tuesday = db.Column(db.Text, nullable=True)
    wednesday = db.Column(db.Text, nullable=True)
    thursday = db.Column(db.Text, nullable=True)

    def __init__(self, issuer_id:int, employee_id:int, monday:Optional[str] = None, tuesday:Optional[str] = None, wednesday:Optional[str] = None, thursday:Optional[str] = None):
        self.issuer_id = issuer_id
        self.employee_id = employee_id
        self.monday = monday
        self.tuesday = tuesday
        self.wednesday = wednesday
        self.thursday = thursday

    def __repr__(self):
        return f'<EmployeeHomeworkRoom {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'datetime': self.datetime,
            'issuer_id': self.issuer_id,
            'employee_id': self.employee_id,
            'monday': self.monday,
            'tuesday': self.tuesday,
            'wednesday': self.wednesday,
            'thursday': self.thursday
        }
    


class EmployeeSchoolClub(db.Model):
    __tablename__ = 'employee_school_clubs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(datetime.UTC))
    issuer_id = db.Column(db.Integer, nullable=False)
    employee_id = db.Column(db.Integer, nullable=False)
    monday_id = db.Column(db.Integer, nullable=True)
    tuesday_id = db.Column(db.Integer, nullable=True)
    wednesday_id = db.Column(db.Integer, nullable=True)
    thursday_id = db.Column(db.Integer, nullable=True)

    def __init__(self, issuer_id:int, employee_id:int, monday_id:Optional[int] = None, tuesday_id:Optional[int] = None, wednesday_id:Optional[int] = None, thursday_id:Optional[int] = None):
        self.issuer_id = issuer_id
        self.employee_id = employee_id
        self.monday_id = monday_id
        self.tuesday_id = tuesday_id
        self.wednesday_id = wednesday_id
        self.thursday_id = thursday_id

    def __repr__(self):
        return f'<EmployeeSchoolClubs {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'datetime': self.datetime,
            'issuer_id': self.issuer_id,
            'employee_id': self.employee_id,
            'monday_id': self.monday_id,
            'tuesday_id': self.tuesday_id,
            'wednesday_id': self.wednesday_id,
            'thursday_id': self.thursday_id
        }
    
class HomeworkRoom(db.Model):
    __tablename__ = 'homework_rooms'
    __table_args__ = {'mysql_charset': 'utf8mb4'}

    id = db.Column(db.Integer, primary_key = True, nullable=False)
    room = db.Column(db.Text, nullable=False)

    def __init__(self, room:str):
        self.room = room

    def __repr__(self):
        return f'<HomeworkRoom {self.id} {self.room}>'

    def to_dict(self):
        return {
            'id': self.id,
            'room': self.room
        }



class SchoolClub(db.Model):
    __tablename__ = 'school_clubs'

    id = db.Column(db.Integer, primary_key = True, nullable=False)
    title = db.Column(db.Text, nullable=False)

    def __init__(self, title:str):
        self.title = title

    def __repr__(self):
        return f'<SchoolClub {self.id} {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title
        }
    


class SchoolClubRoom(db.Model):
    __tablename__ = 'school_club_rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(datetime.UTC))
    issuer_id = db.Column(db.Integer, nullable=False)
    school_club_id = db.Column(db.Integer, nullable=False)
    monday = db.Column(db.Text, nullable=True)
    tuesday = db.Column(db.Text, nullable=True)
    wednesday = db.Column(db.Text, nullable=True)
    thursday = db.Column(db.Text, nullable=True)

    def __init__(self, issuer_id:int, school_club_id:int, monday:Optional[str] = None, tuesday:Optional[str] = None, wednesday:Optional[str] = None, thursday:Optional[str] = None):
        self.issuer_id = issuer_id
        self.school_club_id = school_club_id
        self.monday = monday
        self.tuesday = tuesday
        self.wednesday = wednesday
        self.thursday = thursday

    def __repr__(self):
        return f'<SchoolClubRoom {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'date_time': self.date_time,
            'issuer_id': self.issuer_id,
            'school_club_id': self.school_club_id,
            'monday': self.monday,
            'tuesday': self.tuesday,
            'wednesday': self.wednesday,
            'thursday': self.thursday
        }



class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key = True, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    class_id = db.Column(db.Text, nullable=False)

    def __init__(self, first_name:str, last_name:str, grade:int, class_id:str):
        self.first_name = first_name
        self.last_name = last_name
        self.grade = grade
        self.class_id = class_id

    def __repr__(self):
        return f'<Student {self.id} {self.first_name} {self.last_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'grade': self.grade,
            'class_id': self.class_id
        }



class StudentAbsentIrregular(db.Model):
    __tablename__ = 'student_absence_irregular'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(datetime.UTC))
    issuer_id = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, nullable=False)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)

    def __init__(self, issuer_id: int, student_id: int, start_datetime: datetime.datetime, end_datetime: datetime.datetime):
        self.issuer_id = issuer_id
        self.student_id = student_id
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime

    def __repr__(self):
        return f'<StudentAbsentIrregular {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'date_time': self.date_time,
            'issuer_id': self.issuer_id,
            'student_id': self.student_id,
            'start_datetime': self.start_datetime,
            'end_datetime': self.end_datetime
        }



class StudentAbsentRegular(db.Model):
    __tablename__ = 'student_absence_regular'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(datetime.UTC))
    issuer_id = db.Column(db.Integer, nullable=False)
    start_datetime = db.Column(db.Date, nullable=False)
    end_datetime = db.Column(db.Date, nullable=False)
    student_id = db.Column(db.Integer, nullable=False)
    full_day = db.Column(db.Boolean, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    monday = db.Column(db.Boolean, nullable=False)
    tuesday = db.Column(db.Boolean, nullable=False)
    wednesday = db.Column(db.Boolean, nullable=False)
    thursday = db.Column(db.Boolean, nullable=False)

    def __init__(self, issuer_id: int, start_datetime:datetime.datetime, end_datetime: datetime.datetime, student_id: int, full_day: bool, start_time: datetime.time, end_time: datetime.time, monday: bool, tuesday: bool, wednesday: bool, thursday: bool):
        self.issuer_id = issuer_id
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.student_id = student_id
        self.full_day = full_day
        self.start_time = start_time
        self.end_time = end_time
        self.monday = monday
        self.tuesday = tuesday
        self.wednesday = wednesday
        self.thursday = thursday

    def __repr__(self):
        return f'<StudentAbsentRegular {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'date_time': self.date_time,
            'issuer_id': self.issuer_id,
            'start_datetime': self.start_datetime,
            'end_datetime': self.end_datetime,
            'student_id': self.student_id,
            'full_day': self.full_day,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'monday': self.monday,
            'tuesday': self.tuesday,
            'wednesday': self.wednesday,
            'thursday': self.thursday
        }


class StudentNote(db.Model):
    __tablename__ = "student_notes"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(datetime.UTC))
    issuer_id = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, nullable=False)
    note = db.Column(db.Text, nullable=False)

    def __init__(self, issuer_id:int, student_id:int, note:str):
        self.issuer_id = issuer_id
        self.student_id = student_id
        self.note = note

    def to_dict(self):
        return {
            'id': self.id,
            'datetime': self.datetime,
            'issuer_id': self.issuer_id,
            'student_id': self.student_id,
            'note': self.note,
        }


class StudentHomeworkRoom(db.Model):
    __tablename__ = 'student_homework_room'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(datetime.UTC))
    issuer_id = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, nullable=False)
    monday = db.Column(db.Text, nullable=True)
    tuesday = db.Column(db.Text, nullable=True)
    wednesday = db.Column(db.Text, nullable=True)
    thursday = db.Column(db.Text, nullable=True)

    def __init__(self, issuer_id:int, student_id:int, monday:Optional[str] = None, tuesday:Optional[str] = None, wednesday:Optional[str] = None, thursday:Optional[str] = None):
        self.issuer_id = issuer_id
        self.student_id = student_id
        self.monday = monday
        self.tuesday = tuesday
        self.wednesday = wednesday
        self.thursday = thursday

    def __repr__(self):
        return f'<StudentHomeworkRoom {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'datetime': self.datetime,
            'issuer_id': self.issuer_id,
            'student_id': self.student_id,
            'monday': self.monday,
            'tuesday': self.tuesday,
            'wednesday': self.wednesday,
            'thursday': self.thursday
        }



class StudentSchoolClub(db.Model):
    __tablename__ = 'student_school_clubs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(datetime.UTC))
    issuer_id = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, nullable=False)
    monday_id = db.Column(db.Integer, nullable=True)
    tuesday_id = db.Column(db.Integer, nullable=True)
    wednesday_id = db.Column(db.Integer, nullable=True)
    thursday_id = db.Column(db.Integer, nullable=True)

    def __init__(self, issuer_id:int, student_id:int, monday_id:Optional[int] = None, tuesday_id:Optional[int] = None, wednesday_id:Optional[int] = None, thursday_id:Optional[int] = None):
        self.issuer_id = issuer_id
        self.student_id = student_id
        self.monday_id = monday_id
        self.tuesday_id = tuesday_id
        self.wednesday_id = wednesday_id
        self.thursday_id = thursday_id

    def __repr__(self):
        return f'<StudentSchoolClubs {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'datetime': self.datetime,
            'issuer_id': self.issuer_id,
            'student_id': self.issuer_id,
            'monday_id': self.monday_id,
            'tuesday_id': self.tuesday_id,
            'wednesday_id': self.wednesday_id,
            'thursday_id': self.thursday_id
        }
