import random
import string
import bcrypt
from flask import Flask
from sqlalchemy.event import listens_for
import pandas as pd

import os

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, Employee, audit
import Secrets

file = f"../Secrets/{Secrets.fileNameTeachers}"
file = os.path.join(os.path.dirname(os.path.abspath(__file__)), file)
print(file)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = Secrets.database_uri.replace(Secrets._database_host, "192.168.2.102:3307")

db.init_app(app)

@listens_for(db.session, "after_flush")
def add_audit_entries(session, flush_context):
    audit.audit_listener(session, flush_context, None, None)

def generate_password(length:int, charUpper:bool = True, charLower:bool = True, digits:bool = True, symbols:bool = True):
    if length <= 0:
        raise ValueError(f"lentgh must be above 0: {length}")
    if not (charUpper or charLower or digits or symbols):
        raise ValueError(f"at least one of the following parameters must be True: charUpper({charUpper}), charLower({charLower}), digits({digits}), symbols({symbols})")

    chars = ""
    if charUpper: chars += string.ascii_uppercase
    if charLower: chars += string.ascii_lowercase
    if digits: chars += string.digits
    if symbols: chars += string.punctuation

    ambiguous_chars = 'Il1O0'
    chars = ''.join([c for c in chars if c not in ambiguous_chars])

    password = ''.join(random.choice(chars) for _ in range(length))
    return password

df = pd.read_excel(file,usecols=[0, 1, 2, 3], header=1, dtype={0: str, 1: str, 2: str, 3:str})

passwords = []
count = 0
skipped = 0
with app.app_context():
    for index, row in df.iterrows():
        r = list(row.values)
        for c in range(len(r)):
            if r[c] == "":
                r[c] = None
            
        #print(f"short_name: {r[0]}, prefix: {r[1]}, last_name: {r[2]}, first_name: {r[3]}")
        data = {}
        data["short_name"] = r[0]
        data["prefix"] = r[1]
        data["first_name"] = r[3]
        data["last_name"] = r[2]
        data["sec_lvl"] = 1

        employee = Employee.query.filter_by(short_name=data["short_name"]).first()
        if employee != None:
            skipped += 1
            continue

        password = Secrets.first_time_password # um generator zu aktivieren hier None einsetzen
        while password == None and password not in passwords:
            password = generate_password(8)
        passwords.append(password)
        data["password"] = bcrypt.hashpw(bytes(password, "UTF-8"), bcrypt.gensalt())

        print("-"*100)
        print(data)
        
        employeeNew = Employee(**data,
                    monday_homework_room_id=None, tuesday_homework_room_id=None, wednesday_homework_room_id=None, thursday_homework_room_id=None,
                    monday_school_club_id=None, tuesday_school_club_id=None, wednesday_school_club_id=None, thursday_school_club_id=None, password_change_recomended=True)
        count += 1
        db.session.add(employeeNew)
    
    print("-"*100)
    print(f"{count} werden Angestellte hinzugefügt, {skipped} wurden übersprungen da sie bereits existierten")

    if count == 0:
        print("Keine Änderungen gespeichert")
    else:
        i = input("Änderungen bestätigen(\"commit\") oder verwerfen(\"\"): ")
        if i == "commit":
            db.session.commit()
            print("änderungen gespeichert")