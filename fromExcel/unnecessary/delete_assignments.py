from typing import cast
from flask import Flask
from sqlalchemy.event import listens_for
import os

file = "../Secrets/teachers.xlsx"
file = os.path.join(os.path.dirname(os.path.abspath(__file__)), file)
print(file)

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, Employee, Student, audit
import Secrets

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = Secrets.database_uri.replace(Secrets._database_host, "192.168.2.102:3307")

db.init_app(app)

@listens_for(db.session, "after_flush")
def add_audit_entries(session, flush_context):
    audit.audit_listener(session, flush_context, None, None)

with app.app_context():
    for employee in Employee.query.all():
        employee = cast(Employee, employee)
        employee.monday_homework_room_id = None
        employee.tuesday_homework_room_id = None
        employee.wednesday_homework_room_id = None
        employee.thursday_homework_room_id = None
        employee.monday_school_club_id = None
        employee.tuesday_school_club_id = None
        employee.wednesday_school_club_id = None
        employee.thursday_school_club_id = None

    for student in Student.query.all():
        student = cast(Student, student)
        student.monday_homework_room_id = None
        student.tuesday_homework_room_id = None
        student.wednesday_homework_room_id = None
        student.thursday_homework_room_id = None
        student.monday_school_club_id = None
        student.tuesday_school_club_id = None
        student.wednesday_school_club_id = None
        student.thursday_school_club_id = None

    db.session.commit()