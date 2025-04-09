import random
import pandas as pd
from faker import Faker
fake = Faker("de_DE")

teachersData = [[], [], [], [], [], [], [], [], ["Kürzel", "Bezeichnung", "Lehrer", "Raum", None, "Raum", "Lehrer - Mo", None, "Raum", "Lehrer - Die", None, "Raum", "Lehrer - Mi", None, "Raum", "Lehrer - Do"]]
haRooms = ["130", "131", "132", "133", "137", "138", "139"]
ags = [
    ["BaMo", "Badminton Montag", "SP2"],
    ["Fit", "Fitness für Mädchen", "SP3"],
    ["FF", "Französischförderunterricht 6-8", "139"],
    ["GSMo", "Gesellschaftsspiele Montag", "036"],
    ["SuH", "Stricken und Häkeln", "131"],
    ["TS", "Tastaturschreiben", "101"],
    ["ThTa", "Think tank", "132"],
    ["FBDie", "Fußball Dienstag", "SP1"],
    ["TTDie", "Tischtennis Dienstag", "SP3"],
    ["BVB", "Volleyball", "SP2"],
    ["HS", "Hörspiele", "138"],
    ["IT", "Improvisationstheater", "133"],
    ["RKS", "Rätsel- und Knobelspiele", "132"],
    ["LB", "Mit Liebe gebastelt", "137"],
    ["BaMi", "Badminton Mittwoch", "SP1"],
    ["BS", "Ballspiele", "SP2"],
    ["TTMi", "Tischtennis Mittwoch", "SP3"],
    ["EF", "Englischförderunterricht 6-8", "130"],
    ["MF", "Matheförderunterricht 6-8", "139"],
    ["GSMi", "Gesellschaftsspiele Mittwoch", "036"],
    ["IS", "Interaktive Spiele", "132"],
    ["BSp", "Ballsport", "SP3"],
    ["FBDo", "Fußball Donnerstag", "SP1"],
    ["DF", "Deutschförderunterricht 6-8", "130"],
    ["GSDo", "Gesellschaftsspiele Donnerstag", "036"],
    ["HL", "Handlettering", "133"],
    ["LM", "Lego Mindstorms", "101"],
    ["SSM", "Singen-Spielen-Musizieren", "322"],
]

for i in range(max(len(haRooms)+1, len(ags))):
    data = [None]*16
    if 0 < i < len(haRooms)+1:
        data[5], data[8], data[11], data[14] = haRooms[i-1], haRooms[i-1], haRooms[i-1], haRooms[i-1]
        t = ["Ack", "Adam", "Adm", "Amb", "Baum", "BauS", "BayA"]
        data[6], data[9], data[12], data[15] = t[i-1], t[i-1], t[i-1], t[i-1]
    if i < len(ags):
        data[0] = ags[i][0]
        data[1] = ags[i][1]
        data[2] = "Ack"
        data[3] = ags[i][2]
    teachersData.append(data)

studentsData = [[None, "Name", "Vorname", "Klasse", None, None, None, "Montag-AG", "Dienstag-AG", "Mittwoch-AG", "Donnerstag-AG", None, None, None, None, "Hausaufgabenraum"]]

for i in range(150):
    klasse = "0" + str(random.randint(5,9)) + random.choice(["a", "b", "c", "d", "e"])
    studentsData.append([None, fake.last_name(), fake.first_name(), klasse, None, None, None, ags[random.randint(0,6)][0], ags[random.randint(7,13)][0], ags[random.randint(14,20)][0], ags[random.randint(21,27)][0], None, None, None, None, random.choice(haRooms)])

teachers = pd.DataFrame(teachersData)
students = pd.DataFrame(studentsData)

with pd.ExcelWriter("Secrets/studentsAndSchoolClubs-fake.xlsx", engine="openpyxl") as writer:
    teachers.to_excel(writer, sheet_name="HJ-Daten", index=False, header=False)
    students.to_excel(writer, sheet_name="Übersicht", index=False, header=False)
