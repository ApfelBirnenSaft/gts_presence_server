import sqlalchemy

def create_audit(mapper, connection:sqlalchemy.engine.base.Connection, target):
    print(type(mapper), mapper)
    print(type(connection), connection)
    print(type(target), target)

from .Employee import *
sqlalchemy.event.listen(Employee, "after_insert", create_audit)
