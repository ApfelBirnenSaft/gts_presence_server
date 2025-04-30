import flask_sqlalchemy

db = flask_sqlalchemy.SQLAlchemy()

from .audit import audit

from .tokens import *

from .employee import *
from .audit.employee_audit import *

from .student import *
from .audit.student_audit import *

from .homeworkRoom import *
from .audit.homeworkRoom_audit import *

from .schoolClub import *
from .audit.schoolClub_audit import *

from .featureRequest import *
from .audit.featureRequest_audit import *