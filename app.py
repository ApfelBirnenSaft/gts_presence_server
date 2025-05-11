from functools import wraps
import typing
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, disconnect, emit, send
from flask_jwt_extended import JWTManager, create_refresh_token, get_jwt, get_jwt_identity, jwt_required, create_access_token, verify_jwt_in_request
from flask_cors import CORS
import bcrypt
from dateutil import parser
import datetime

from sqlalchemy.event import listens_for
from sqlalchemy import and_, or_

from models_old import *
import Secrets

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = Secrets.database_uri_v1
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.secret_key = "shejevt34grtv3qgfvciktr38id1x85t4nqi3rnv45fgz476g5fwu3s45h37sqp3"
cors = CORS(app)

app.config['JWT_SECRET_KEY'] = '23v3bqnv8w34vqo9h8jb4q8cnrtbiuzsb4v3785nw8954tnv7436r738cvnh3487'
jwt = JWTManager(app)

socketio = SocketIO(app, cors_allowed_origins="*", transports=['websocket'])

db.init_app(app)

"""
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None
"""

def create_token_deleting_event_if_not_exists():
    event_name = "delete_expired_tokens"
    
    check_event_sql = "SELECT COUNT(*) FROM information_schema.EVENTS WHERE EVENT_SCHEMA = DATABASE() AND EVENT_NAME = \"" + event_name + "\" and STATUS = \"ENABLED\";"

    create_event_sql = "CREATE EVENT " + event_name + " ON SCHEDULE EVERY 1 HOUR DO DELETE FROM tokens WHERE expires_at < NOW();"

    with app.app_context():
        result = db.session.execute(db.text(check_event_sql))
        event_exists = result.fetchone()[0] > 0

        if not event_exists:
            db.session.execute(db.text(create_event_sql))
            db.session.commit()
            print(f"Event '{event_name}' wurde erstellt.")
        else:
            print(f"Event '{event_name}' existiert bereits.")

@listens_for(db.session, "after_flush")
def add_audit_entries(session, flush_context):
    audit.audit_listener(session, flush_context, get_jwt_identity, socketio)

def min_sec_lvl_required(min_lvl:int):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            return check_min_sec_lvl(min_lvl, fn, *args, **kwargs)
        return decorator
    return wrapper

def check_min_sec_lvl(min_lvl:int, fn = None, *args, **kwargs):
    verify_jwt_in_request()
    user = Employee.query.get(get_jwt_identity())
    if not isinstance(user, Employee):
        return jsonify(msg="user not found (user may got removed)"), 404
    print(f"user: {user.sec_lvl}, min_lvl: {min_lvl}, result: {user.sec_lvl >= min_lvl}")
    if user.sec_lvl >= min_lvl:
        return None if fn == None else fn(*args, **kwargs)
    else:
        return jsonify(msg="Higher security level is required"), 403

@app.route('/login', methods=['POST'])
def login():
    short_name = request.json.get('short_name', None)
    password = request.json.get('password', None)

    if short_name == None or password == None:
        return jsonify(msg="missing short name or password"), 404
    user = Employee.query.filter_by(short_name=short_name).first()
    if not isinstance(user, Employee) or not bcrypt.checkpw(bytes(password, "UTF-8"), bytes(user.password, "UTF-8")):
        return jsonify(msg="wrong short_name or password"), 403
        
    access_token = create_access_token(identity=user.id, expires_delta=datetime.timedelta(minutes=60))
    refresh_token = create_refresh_token(identity=user.id, expires_delta=datetime.timedelta(days=30))

    return jsonify(access_token=access_token, refresh_token=refresh_token, user=user.to_dict(password_change_recomended_null=False))

@app.route('/refresh', methods=['GET'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    user = Employee.query.filter_by(id=current_user).first()
    if not isinstance(user, Employee):
        return jsonify(msg="user not found (user may got removed)"), 404
    new_access_token = create_access_token(identity=current_user, expires_delta=datetime.timedelta(minutes=60))

    return jsonify(access_token=new_access_token, user=user.to_dict(password_change_recomended_null=False)), 200

# must be changed that it searches the newest entry in every audit entry and gives back the newest (bzw just the date)
#@app.route(rule="/last_data_version", methods = ["GET"])
#@jwt_required()
#def last_data_version():
#    return LastChange.query.first().to_dict()

#emits the current data version datetime
#@app.route(rule="/emit", methods = ["GET"])
#def emit_latest():
#    socketio.emit("data",{"last_data_change": datetime.datetime.now().isoformat(),})
#    return datetime.datetime.now().isoformat()

@app.route(rule="/trigger_data_refresh", methods = ["GET"])
@jwt_required()
@min_sec_lvl_required(3)
def trigger_data_refresh():
    socketio.emit("data",{"last_data_change": datetime.datetime.now().isoformat(),})
    return jsonify(msg="success")

@app.route(rule="/load_data/<string:current_version_datetime>", methods = ["GET"])
@jwt_required()
@min_sec_lvl_required(0)
def load_data(current_version_datetime:str):
    currentDatetime = parser.isoparse(current_version_datetime) - datetime.timedelta(seconds=10)
    today = datetime.datetime.combine(date=datetime.date.today(), time=datetime.time())

    employees = Employee.query.order_by(Employee.last_change.desc()).filter(Employee.last_change > currentDatetime)

    students = Student.query.order_by(Student.last_change.desc()).filter(Student.last_change > currentDatetime)
    student_notes = StudentNote.query.order_by(StudentNote.datetime.desc()).filter(StudentNote.datetime > currentDatetime)
    student_homework_room_presence_state = StudentHomeworkRoomPresence.query.order_by(StudentHomeworkRoomPresence.datetime.desc()).filter(StudentHomeworkRoomPresence.datetime > max(currentDatetime, today))
    student_school_club_presence_state = StudentSchoolClubPresence.query.order_by(StudentSchoolClubPresence.datetime.desc()).filter(StudentSchoolClubPresence.datetime > max(currentDatetime, today))
    student_absence_regular = StudentAbsentRegular.query.order_by(StudentAbsentRegular.created_at.desc(), StudentAbsentRegular.deleted_at.desc()).filter(or_(StudentAbsentRegular.created_at > currentDatetime, and_(StudentAbsentRegular.deleted_at != None,StudentAbsentRegular.deleted_at > currentDatetime)))
    student_absence_irregular = StudentAbsentIrregular.query.order_by(StudentAbsentIrregular.created_at.desc(), StudentAbsentIrregular.deleted_at.desc()).filter(or_(StudentAbsentIrregular.created_at > currentDatetime, and_(StudentAbsentIrregular.deleted_at != None,StudentAbsentIrregular.deleted_at > currentDatetime)))

    homework_rooms = HomeworkRoom.query.order_by(HomeworkRoom.last_change.desc()).filter(HomeworkRoom.last_change > currentDatetime)

    school_clubs = SchoolClub.query.order_by(SchoolClub.last_change.desc()).filter(SchoolClub.last_change > currentDatetime)

    feature_requests = FeatureRequest.query.order_by(FeatureRequest.last_change.desc()).filter(FeatureRequest.last_change > currentDatetime)

    data_changes = [dtObj.datetime if dtObj != None else currentDatetime for dtObj in [
                        student_notes.first(),
                        student_homework_room_presence_state.first(),
                        student_school_club_presence_state.first(),
                    ]]
    date = feature_requests.first()
    if isinstance(date, FeatureRequest):
        data_changes.append(date.last_change)
    date = student_absence_regular.first()
    if isinstance(date, StudentAbsentRegular):
        if date.deleted_at != None:
            data_changes.append(date.deleted_at)
        data_changes.append(date.created_at)
    date = student_absence_irregular.first()
    if isinstance(date, StudentAbsentIrregular):
        if date.deleted_at != None:
            data_changes.append(date.deleted_at)
        data_changes.append(date.created_at)

    last_data_change = max(data_changes)

    user_id = get_jwt_identity()

    if isinstance(last_data_change, datetime.datetime):
        last_data_change = last_data_change.isoformat()
    else:
        last_data_change = currentDatetime.isoformat()

    return {
        "last_data_change": last_data_change,
        "employees": [obj.to_dict(password_change_recomended_null = obj.id != user_id) for obj in employees],
        "students": [obj.to_dict() for obj in students],
        "student_notes": [obj.to_dict() for obj in student_notes],
        "student_homework_room_presence_state": [obj.to_dict() for obj in student_homework_room_presence_state],
        "student_school_club_presence_state": [obj.to_dict() for obj in student_school_club_presence_state],
        "student_absence_regular": [obj.to_dict() for obj in student_absence_regular],
        "student_absence_irregular": [obj.to_dict() for obj in student_absence_irregular],
        "homework_rooms": [obj.to_dict() for obj in homework_rooms],
        "school_clubs": [obj.to_dict() for obj in school_clubs],
        "feature_requests": [obj.to_dict() for obj in feature_requests],
    }

@app.route(rule="/student_note", methods = ["POST"])
@jwt_required()
@min_sec_lvl_required(1)
def post_student_note():
    note = request.json.get('note', None)
    issuer_id = get_jwt_identity()
    student_id = request.json.get('student_id', None)

    if note == None or student_id == None:
        return jsonify(msg="missing note or student_id"), 404
    
    studentNote = StudentNote(issuer_id=issuer_id, note=note, student_id=student_id)
    db.session.add(studentNote)
    db.session.commit()

    socketio.emit("data",{"last_data_change": studentNote.datetime.isoformat(),})

    return jsonify(msg="success")

@app.route(rule="/student_presence", methods = ["POST"])
@jwt_required()
@min_sec_lvl_required(1)
def post_student_presence():
    presence_states = request.json
    data_changes = []
    sec_lvl_2_check = False
    for presence_state in presence_states:
        state = PresenceState.from_string(presence_state.get('presence_state', None))
        issuer_id = get_jwt_identity()
        student_id = presence_state.get('student_id', None)
        from_activity_string_id = presence_state.get('from_activity_string_id', None)
        presence_type = presence_state.get('presence_type', None)
        date_time = None if presence_state.get('datetime', None) == None else datetime.datetime.fromisoformat(presence_state.get('datetime', None)).astimezone(datetime.timezone.utc)

        if state == None or student_id == None or presence_type == None:
            return jsonify(msg="missing presence_state or student_id"), 404
        
        if not sec_lvl_2_check and not state in [PresenceState.Present, PresenceState.Missing]:
            sec_lvl_2_check = True
        
        if presence_type == "homeworkRoom":
            studentPresence = StudentHomeworkRoomPresence(issuer_id=issuer_id, presence_state=state, student_id=student_id, from_activity_string_id=from_activity_string_id, datetime=date_time)
        else:
            studentPresence = StudentSchoolClubPresence(issuer_id=issuer_id, presence_state=state, student_id=student_id, from_activity_string_id=from_activity_string_id, datetime=date_time)
        data_changes.append(studentPresence.datetime)
        db.session.add(studentPresence)

    if sec_lvl_2_check:
        sec_check = check_min_sec_lvl(2)
        if sec_check != None: return sec_check

    db.session.commit()

    if data_changes != []:
        socketio.emit("data",{"last_data_change": max(data_changes).isoformat(),})

    return jsonify(msg="success")

@app.route(rule="/add_student_absence_regular", methods = ["POST"])
@jwt_required()
@min_sec_lvl_required(3)
def post_student_absence_regular():
    print(request.json)
    data = request.json
    created_at = datetime.datetime.fromisoformat(data['created_at'])
    
    valid_from = datetime.date.fromisoformat(data['valid_from'])
    
    valid_until = datetime.date.fromisoformat(data['valid_until']) if data.get('valid_until') else None
    
    start_time = datetime.time.fromisoformat(data['start_time'])
    end_time = datetime.time.fromisoformat(data['end_time'])
    
    created_by_id = get_jwt_identity()
    
    # Rückgabe einer Instanz von StudentAbsentRegular
    absence = StudentAbsentRegular(
        valid_from=valid_from,
        valid_until=valid_until,
        student_id=data['student_id'],
        start_time=start_time,
        end_time=end_time,
        monday=data['monday'],
        tuesday=data['tuesday'],
        wednesday=data['wednesday'],
        thursday=data['thursday'],
        created_at=created_at,
        created_by_id=created_by_id,
    )
    
    db.session.add(absence)
    db.session.commit()

    socketio.emit("data",{"last_data_change": absence.created_at.isoformat(),})

    return jsonify(msg="success")

@app.route(rule="/delete_student_absence_regular", methods = ["POST"])
@jwt_required()
@min_sec_lvl_required(3)
def delete_student_absence_regular():
    print(request.json)
    data = request.json
    id = data['id']
    user_id = get_jwt_identity()
    
    absence = StudentAbsentRegular.query.get(id)

    if not isinstance(absence, StudentAbsentRegular): return jsonify(msg="entry not found in database"), 404
    
    now = datetime.datetime.now()
    absence.deleted_at = now
    absence.deleted_by_id = user_id
    
    db.session.commit()

    socketio.emit("data",{"last_data_change": datetime.datetime.now().isoformat(),})

    return jsonify(msg="success")

@app.route(rule="/add_student_absence_irregular", methods = ["POST"])
@jwt_required()
@min_sec_lvl_required(3)
def post_student_absence_irregular():
    print(request.json)
    data = request.json
    created_at = datetime.datetime.fromisoformat(data['created_at'])
    
    start_datetime = datetime.datetime.fromisoformat(data['start_datetime'])
    
    end_datetime = datetime.datetime.fromisoformat(data['end_datetime'])

    student_id = data['student_id']
    
    created_by_id = get_jwt_identity()
    
    absence = StudentAbsentIrregular(
        student_id=student_id,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        created_at=created_at,
        created_by_id=created_by_id,
    )
    
    db.session.add(absence)
    db.session.commit()

    socketio.emit("data",{"last_data_change": absence.created_at.isoformat(),})

    return jsonify(msg="success")

@app.route(rule="/delete_student_absence_irregular", methods = ["POST"])
@jwt_required()
@min_sec_lvl_required(3)
def delete_student_absence_irregular():
    print(request.json)
    data = request.json
    id = data['id']
    user_id = get_jwt_identity()
    
    absence = StudentAbsentIrregular.query.get(id)

    if not isinstance(absence, StudentAbsentIrregular): return jsonify(msg="entry not found in database"), 404
    
    now = datetime.datetime.now()
    absence.deleted_at = now
    absence.deleted_by_id = user_id
    
    db.session.commit()

    socketio.emit("data",{"last_data_change": datetime.datetime.now().isoformat(),})

    return jsonify(msg="success")


@app.route(rule="/change_password", methods = ["POST"])
@jwt_required()
@min_sec_lvl_required(0)
def change_password():
    data = request.json
    password = data['password']
    new_password = data['new_password']
    user_id = get_jwt_identity()
    
    user = Employee.query.get(user_id)

    if not isinstance(user, Employee): return jsonify(msg="user not found"), 404
    if not bcrypt.checkpw(bytes(password, "UTF-8"), bytes(user.password, "UTF-8")):
        return jsonify(msg="wrong password"), 403

    user.password = new_password
    user.password_change_recomended = False
    
    db.session.commit()

    socketio.emit("data",{"last_data_change": datetime.datetime.now().isoformat(),})

    return jsonify(msg="success")


@app.route(rule="/reset_password", methods = ["POST"])
@jwt_required()
@min_sec_lvl_required(2)
def reset_password():
    data = request.json
    password = data['password']
    target_id = data['target_id']
    issuer_id = get_jwt_identity()
    
    target = Employee.query.get(target_id)
    issuer = Employee.query.get(issuer_id)

    if not isinstance(target, Employee):
        return jsonify(msg="password reset target not found"), 404
    if not isinstance(issuer, Employee):
        return jsonify(msg="password reset issuer not found"), 404
    
    sec_check = check_min_sec_lvl(target.sec_lvl)
    if sec_check != None: return sec_check

    if not bcrypt.checkpw(bytes(password, "UTF-8"), bytes(issuer.password, "UTF-8")):
        return jsonify(msg="wrong password"), 403

    initPw = Secrets.first_time_password
    target.password = bcrypt.hashpw(bytes(initPw, "UTF-8"), bcrypt.gensalt())
    target.password_change_recomended = True
    
    db.session.commit()

    return jsonify(msg="success", initPw=initPw)

"""
@app.route(rule="/fRs", methods = ["GET"])
def get_feature_requests():
    fRs = FeatureRequest.query.filter(FeatureRequest.parent_id == None).all()
    return [fRs[i].to_dict() for i in range(len(fRs))]
"""

@app.route(rule="/delete_student_note", methods = ["POST"])
@jwt_required()
@min_sec_lvl_required(1)
def delete_student_note():
    user = db.session.get(Employee, get_jwt_identity())
    if not isinstance(user, Employee): return jsonify(msg="user not found"), 404
    data = request.json
    student_note_id = data['student_note_id']

    student_note = db.session.get(StudentNote, student_note_id)
    if not isinstance(student_note, StudentNote): return jsonify(msg="student note to delete not found"), 404

    if user.id != student_note.issuer_id: return jsonify("use the account of the issuer of this student_note"), 403

    db.session.delete(student_note)
    db.session.commit()

    return jsonify(msg="success")

@app.route(rule="/update_student_note", methods = ["POST"])
@jwt_required()
@min_sec_lvl_required(1)
def update_student_note():
    data = request.json
    student_note_id = data['student_note_id']
    new_note = data['new_note']

    student_note = db.session.get(StudentNote, student_note_id)
    if not isinstance(student_note, StudentNote): return jsonify(msg="student note to update not found"), 404

    student_note.note = new_note
    db.session.commit()

    return jsonify(msg="success")

@app.route(rule="/update_student", methods = ["POST"])
@jwt_required()
@min_sec_lvl_required(3)
def update_student():
    data = request.json
    password = data['password']
    target_id = data['target_id']

    return jsonify(msg="success")

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    create_token_deleting_event_if_not_exists()
    socketio.run(app, host = Secrets.server_host_v1, port = Secrets.server_port_v1, debug = True)#, ssl_context=('certificate/server.crt', 'certificate/private.key'))#, use_reloader=False)