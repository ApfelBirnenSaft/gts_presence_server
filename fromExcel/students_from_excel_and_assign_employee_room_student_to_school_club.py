from typing import cast
import colorama
from flask import Flask
from sqlalchemy.event import listens_for
import pandas as pd

import os

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, SchoolClub, Employee, Student, HomeworkRoom,audit
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

with app.app_context():
   input("Lösche alte Zuweisungen...")
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

   input("Lehrer werden HA Räumen zugewiesen...")

   df = pd.read_excel(file,
      sheet_name="HJ-Daten",
      keep_default_na=False,
      na_values=[None],
      header=8)
   
   count = 0
   for index, row in df.iterrows():
      r = list(row.values)
      for c in range(len(r)):
         if r[c] == "":
            r[c] = None
    
      entries_raw = [[r[5], r[6]], [r[8], r[9]], [r[11], r[12]], [r[14], r[15]]]

      for i in range(len(entries_raw)):
         entry_raw = entries_raw[i]
         if None in entry_raw:
            continue
         room = HomeworkRoom.query.filter_by(room=entry_raw[0]).first()
         if room == None:
            room = HomeworkRoom(room=entry_raw[0])
            db.session.add(room)
         
         employee = Employee.query.filter_by(short_name=entry_raw[1]).first()
         if employee == None or not isinstance(employee, Employee):
            print("-"*100)
            print(f"Ungültiges Angestellten Kürzel: Raum \"{entry_raw[0]}\", Angestellten Kürzel \"{entry_raw[1]}\"")
            continue
         
         if i == 0:
            employee.monday_homework_room_id = room.id
            print("-"*100)
            print(f"Hausaufgaben Raum \"{room.room}\" Aufseher \"{employee.short_name}\" für Montag zugeteilt")
            count += 1
         elif i == 1:
            employee.tuesday_homework_room_id = room.id
            print("-"*100)
            print(f"Hausaufgaben Raum \"{room.room}\" Aufseher \"{employee.short_name}\" für Dienstag zugeteilt")
            count += 1
         elif i == 2:
            employee.wednesday_homework_room_id = room.id
            print("-"*100)
            print(f"Hausaufgaben Raum \"{room.room}\" Aufseher \"{employee.short_name}\" für Mittwoch zugeteilt")
            count += 1
         elif i == 3:
            employee.thursday_homework_room_id = room.id
            print("-"*100)
            print(f"Hausaufgaben Raum \"{room.room}\" Aufseher \"{employee.short_name}\" für Donnerstag zugeteilt")
            count += 1

   input(f"{count} Lehrer HA Räumen zugewiesen\nfinde Lehrer von AGs...")

   count = 0
   AGs = {}
   for index, row in df.iterrows():
      r = list(row.values)
      for c in range(len(r)):
         if r[c] == "":
            r[c] = None

      if r[0] == None:
         break

      schoolClub = SchoolClub.query.filter_by(short=r[0]).first()
      employee = Employee.query.filter_by(short_name=r[2]).first()
      
      room = r[3]

      while not isinstance(schoolClub, SchoolClub):
         print(f"unbekante ag: {r[0]}")
         sId = input("AG id (\"skip\" zum überspringen): ")
         if sId == "skip":
               print("Übersprungen")
               break
         schoolClub = SchoolClub.query.get(int(sId))
      if not isinstance(schoolClub, SchoolClub): continue
      while not isinstance(employee, Employee):
         print(f"unbekannter angestellter: {r[2]}")
         eId = input("Angestellten id (\"skip\" zum überspringen): ")
         if eId == "skip":
               print("Übersprungen")
               break
         employee = Employee.query.get(int(eId))
      if not isinstance(employee, Employee): continue
      
      AGs[schoolClub.short] = {
         "school_club_id": schoolClub.id,
         "employee_id": employee.id,
         "room": room,
      }

      print("-"*100)
      print(f"AG \"{schoolClub.title}\", Aufseher \"{employee.short_name}\", Raum \"{room}\"")
      count += 1

   print("-"*100)

   input(f"{count} AG/Lehrer zuteilungen gefunden. Weiter zur Zuteilung zu Schülern und Wochentagen...")

   print("-"*100)

   df = pd.read_excel(file,
      sheet_name="Übersicht",
      keep_default_na=False,
      na_values=[None],
      header=0,)

   count = 0
   errors = []
   for index, row in df.iterrows():
      r = list(row.values)
      for c in range(len(r)):
         if r[c] == "":
            r[c] = None

      if r[1] == None or r[2] == None:
         break
      
      data = {}
      data["first_name"] = r[2]
      data["last_name"] = r[1]

      klasse = r[3]
      data["grade"] = int(klasse[:2])
      data["class_id"] = klasse[2:]

      room = HomeworkRoom.query.filter_by(room=r[15]).first()
      if room == None:
         room = HomeworkRoom(room=r[15])
         db.session.add(room)
         #db.session.commit()
      data["monday_homework_room_id"] = room.id
      data["tuesday_homework_room_id"] = room.id
      data["wednesday_homework_room_id"] = room.id
      data["thursday_homework_room_id"] = room.id

      weekDays = ["monday", "tuesday", "wednesday", "thursday"]
      for i in range(4):
         index = 7+i
         weekDay = weekDays[i]
         if r[index] == None or r[index] == "e":
            data[f"{weekDay}_school_club_id"] = None
         else:
            if r[index] in AGs:
               club = SchoolClub.query.get(AGs[r[index]]["school_club_id"])
               while club == None:
                  print(f"AG {AGs[r[index]]["school_club_id"]} nicht gefunden")
                  cId = input("AG id (\"skip\" zum überspringen): ")
                  if cId == "skip":
                     print("Übersprungen")
                     break
                  club = SchoolClub.query.get(int(cId))

               employee = Employee.query.get(AGs[r[index]]["employee_id"])
               while employee == None:
                  print(f"Angestellter {r[index]} nicht gefunden")
                  eId = input("Angestellten id (\"skip\" zum überspringen): ")
                  if eId == "skip":
                     print("Übersprungen")
                     break
                  eIemployeed = Employee.query.get(int(eId))
               
               room = AGs[r[index]]["room"]

               if isinstance(club, SchoolClub) and isinstance(employee, Employee):
                  if i == 0:
                     employee.monday_school_club_id = club.id
                     club.room_monday = room
                  elif i == 1:
                     employee.tuesday_school_club_id = club.id
                     club.room_tuesday = room
                  elif i == 2:
                     employee.wednesday_school_club_id = club.id
                     club.room_wednesday = room
                  elif i == 3:
                     employee.thursday_school_club_id = club.id
                     club.room_thursday = room
                  #db.session.commit()
                  
            else:
               txt = f"{colorama.Fore.RED} für schüler/ag/angestellten fehlgeschlagen einander zuzuweißen !!!manuel nachholen!!!\nWochentag {weekDay}, Schüler {data["first_name"]} {data["last_name"]}, AG {r[index]}{colorama.Style.RESET_ALL}"
               print(txt)
               errors.append(txt)
            if club != None:
               data[f"{weekDay}_school_club_id"] = club.id
      
      print("-"*100)
      print(data)
      newStudent = Student(**data)
      student = Student.query.filter_by(
         first_name = newStudent.first_name,
         last_name = newStudent.last_name,
         grade = newStudent.grade,
         class_id = newStudent.class_id,
         ).first()
      if isinstance(student, Student):
         student.monday_homework_room_id = newStudent.monday_homework_room_id
         student.tuesday_homework_room_id = newStudent.tuesday_homework_room_id
         student.wednesday_homework_room_id = newStudent.wednesday_homework_room_id
         student.thursday_homework_room_id = newStudent.thursday_homework_room_id

         student.monday_school_club_id = newStudent.monday_school_club_id
         student.tuesday_school_club_id = newStudent.tuesday_school_club_id
         student.wednesday_school_club_id = newStudent.wednesday_school_club_id
         student.thursday_school_club_id = newStudent.thursday_school_club_id
      else:
         db.session.add(newStudent)
      count += 1
      #db.session.commit()

   print("-"*100)
   print(f"{count} Schüler hinzugefügt")
   print("-"*100)
   print(f"{len(errors)} Fehler sind bezüglich AG/Raum/Schüler/Angestellten zuweisung entstanden. Bitte Manuel Überprüfen:")
   for e in errors:
      print("-"*100)
      print(e)
   
   i = input("Änderungen bestätigen(\"commit\") oder verwerfen(\"\"): ")
   if i == "commit":
      db.session.commit()
      print("änderungen gespeichert")