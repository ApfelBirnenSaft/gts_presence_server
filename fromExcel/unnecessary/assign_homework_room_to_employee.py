from flask import Flask
from sqlalchemy.event import listens_for
import pandas as pd

import os

file = "../Secrets/studentsAndSchoolClubs.xlsx"
file = os.path.join(os.path.dirname(os.path.abspath(__file__)), file)
print(file)

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, HomeworkRoom, Employee, audit
import Secrets

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = Secrets.database_uri

db.init_app(app)

@listens_for(db.session, "after_flush")
def add_audit_entries(session, flush_context):
    audit.audit_listener(session, flush_context, None, None)

df = pd.read_excel(file,
    sheet_name="HJ-Daten",
    keep_default_na=False,
    na_values=[None],
    header=9)

count = 0
for index, row in df.iterrows():
    r = list(row.values)
    for c in range(len(r)):
       if r[c] == "":
          r[c] = None

    if len(r) < 16 or not ( (r[5] != None and r[6] != None) or (r[8] != None and r[9] != None) or (r[11] != None and r[12] != None) or (r[14] != None and r[15] != None) ):
        break

    with app.app_context():
        entries_raw = [[r[5], r[6]], [r[8], r[9]], [r[11], r[12]], [r[14], r[15]]]

        for i in range(len(entries_raw)):
            entry_raw = entries_raw[i]
            if entry_raw[0] == None or entry_raw[1] == None:
                continue
            room = HomeworkRoom.query.filter_by(room=entry_raw[0]).first()
            if room == None:
                room = HomeworkRoom(room=entry_raw[0])
            
            employee = Employee.query.filter_by(short_name=entry_raw[1]).first()
            if employee == None or not isinstance(employee, Employee):
                print("-"*100)
                print(f"Ungültiges Angestellten Kürzel: Raum \"{entry_raw[0]}\", Angestellten Kürzel \"{entry_raw[1]}\"")
                continue
            
            if i == 0:
                db.session.add(room)
                employee.monday_homework_room_id = room.id
                print("-"*100)
                print(f"Hausaufgaben Raum \"{room.room}\" Aufseher \"{employee.short_name}\" für Montag zugeteilt")
                count += 1
            if i == 1:
                db.session.add(room)
                employee.tuesday_homework_room_id = room.id
                print("-"*100)
                print(f"Hausaufgaben Raum \"{room.room}\" Aufseher \"{employee.short_name}\" für Dienstag zugeteilt")
                count += 1
            if i == 2:
                db.session.add(room)
                employee.wednesday_homework_room_id = room.id
                print("-"*100)
                print(f"Hausaufgaben Raum \"{room.room}\" Aufseher \"{employee.short_name}\" für Mittwoch zugeteilt")
                count += 1
            if i == 3:
                db.session.add(room)
                employee.thursday_homework_room_id = room.id
                print("-"*100)
                print(f"Hausaufgaben Raum \"{room.room}\" Aufseher \"{employee.short_name}\" für Donnerstag zugeteilt")
                count += 1

        db.session.commit()

print("-"*100)
print(f"{count} Hausaufgaben Räume/Angestellte einander zugeteilt")