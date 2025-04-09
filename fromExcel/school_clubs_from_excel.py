from flask import Flask
from sqlalchemy.event import listens_for
import pandas as pd

import os

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, SchoolClub, audit
import Secrets

file = f"../Secrets/{Secrets.fileNameStudentsAgHaAssignment}"
file = os.path.join(os.path.dirname(os.path.abspath(__file__)), file)
print(file)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = Secrets.database_uri.replace(Secrets._database_host, "192.168.2.102:3307")

db.init_app(app)

@listens_for(db.session, "after_flush")
def add_audit_entries(session, flush_context):
    audit.audit_listener(session, flush_context, None, None)

df = pd.read_excel(file,
    sheet_name="HJ-Daten",
    keep_default_na=False,
    na_values=[None],
    header=8)

count = 0
with app.app_context():
    for index, row in df.iterrows():
        r = list(row.values)
        for c in range(len(r)):
            if r[c] == "":
                r[c] = None

        if r[0] == None:
            break
        
        data = {}
        data["short"] = r[0]
        data["title"] = r[1]

        print("-"*100)
        print(data)
        schoolClub = SchoolClub(**data)
        #print(student.first_name, student.last_name, str(student.grade)+student.class_id
        db.session.add(schoolClub)
        count += 1
    db.session.commit()

    print("-"*100)
    print(f"{count} AGs hinzugefügt")