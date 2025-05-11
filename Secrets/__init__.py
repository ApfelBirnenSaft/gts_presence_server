from sqlalchemy import URL


_database_password = "NV5uqJ96Za8buTyM"
_database_user = "gtsv2_user"
_database_host = "gts-mariadb"
#_database_host = "192.168.2.102"
_database_port = 3306
#_database_port = 3307
_database = "gtsv2"

database_uri_v1 = f"mysql+pymysql://root:iz*&3rmz&*!wL7%40s@{_database_host}/gts?charset=utf8mb4"
database_uri = URL.create("mysql+aiomysql", _database_user, _database_password, _database_host, _database_port, _database, {"charset": "utf8mb4"})

server_host_v1 = "gts-api-v1"
server_host = "gts-api-server-v2"
#server_host = "localhost"
server_port_v1 = 3012
server_port = 3012

first_time_password = "changeMe"

fileNameStudentsAgHaAssignment = "studentsAndSchoolClubs-fake.xlsx"
fileNameTeachers = "teachers.xlsx"