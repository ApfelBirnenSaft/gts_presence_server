def db_column_name(c):
    return f"{c.parent.class_.__tablename__}.{c.name}"

#from .dataChange import *

from .student import *
from .employee import *
from .activity import *
from .session import *

#sqlalchemy.event.listen(Employee, "after_insert", create_audit)
