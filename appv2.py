from functools import wraps
import typing
from flask import Flask, abort, jsonify, request
from flask_socketio import SocketIO, disconnect, emit, send
from flask_jwt_extended import JWTManager, create_refresh_token, get_jwt, get_jwt_identity, jwt_required, create_access_token, verify_jwt_in_request
from flask_cors import CORS
import bcrypt
import datetime
from sqlalchemy.event import listens_for
from sqlalchemy.orm import aliased

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

db = typing.cast(flask_sqlalchemy.SQLAlchemy, db)

db.init_app(app)

@listens_for(db.session, "after_flush")
def add_audit_entries(session, flush_context):
    """
    Fängt Änderungen in der Session ab und erstellt Audit-Einträge.
    """

    try:
        id = get_jwt_identity()
    except:
        id = None

    for obj in session.new:
        audit.create_audit_entry(session, obj, action=audit.AuditAction.INSERT, issuer_id=id)
    for obj in session.dirty:
        audit.create_audit_entry(session, obj, action=audit.AuditAction.UPDATE, issuer_id=id)
    for obj in session.deleted:
        audit.create_audit_entry(session, obj, action=audit.AuditAction.DELETE, issuer_id=id)
    
    socketio.emit("data",{"last_data_change": datetime.datetime.now().isoformat(),})

@app.route(rule="/<int:x>")
def bla(x:int):
    latest_audit_subquery = (
        db.select(
            HomeworkRoomAudit.id.label("employee_id"),
            db.func.max(HomeworkRoomAudit.audit_datetime).label("latest_id")
        )
        .group_by(HomeworkRoomAudit.id)
        .subquery()
    )
    audit_data_subquery = (
        db.select(
            HomeworkRoomAudit.id.label("employee_id"),
            HomeworkRoomAudit.audit_action,
            HomeworkRoomAudit.audit_datetime,
            HomeworkRoomAudit.audit_id,
            HomeworkRoomAudit.audit_issuer_id
        )
        .join(
            latest_audit_subquery,
            db.and_(
                HomeworkRoomAudit.id == latest_audit_subquery.c.employee_id,
                HomeworkRoomAudit.audit_datetime == latest_audit_subquery.c.latest_id
            )
        )
        .subquery()
    )
    query = (
        db.select(
            HomeworkRoom,
            audit_data_subquery.c.audit_action,
            audit_data_subquery.c.audit_datetime,
            audit_data_subquery.c.audit_id,
            audit_data_subquery.c.audit_issuer_id
        )
        .outerjoin(
            audit_data_subquery,
            HomeworkRoom.id == audit_data_subquery.c.employee_id
        )
        .where(
            db.or_(
                audit_data_subquery.c.audit_id > x,
                audit_data_subquery.c.audit_id.is_(None)
            )
        )
    )
    last_change = None
    result = db.session.execute(query)
    columns = result.keys()
    results = result.fetchall()
        
    mapped_results = [dict(zip(columns, [(r.to_dict() if isinstance(r, HomeworkRoom) else str(r) if isinstance(r, AuditAction) else r.isoformat() if isinstance(r, datetime.datetime) else r) for r in row])) for row in results]

    results = []
    for result in mapped_results:
        results.append(result[HomeworkRoom.__name__])
        if last_change == None or (result["audit_id"] != None and (last_change["audit_id"] == None or last_change["audit_id"] < result["audit_id"])):
            last_change = {
                "audit_id": result["audit_id"],
                "audit_datetime": result["audit_datetime"],
                "audit_issuer_id": result["audit_issuer_id"],
                "audit_action": result["audit_action"],
            }
    deleted = getDeleted(x)
    print(len(deleted))
    for d in deleted:
        if last_change == None or d.audit_id > last_change["audit_id"]:
            last_change = d.to_dict(keepData=False, keepId=False)

    return jsonify(
        students = {
            "last_change": last_change,
            "deleted": [d.to_dict(keepData=False) for d in deleted] if x != 0 else [],
            "active": results
        }
    )
    return jsonify(result=[r.to_dict() for r in results])

def getDeleted(x:int) -> list[HomeworkRoomAudit]:
    t1 = db.aliased(HomeworkRoomAudit, name="t1")
    t2 = db.aliased(HomeworkRoomAudit, name="t2")
    subquery = (
        db.select(db.func.max(t2.audit_id))
        .where(t2.id == t1.id)
        .scalar_subquery()
    )

    query = (
        db.select(t1)
        .where(
            t1.audit_id == subquery,
            t1.audit_action == "DELETE",
            t1.audit_id > x
        )
        .order_by(db.desc(t1.audit_id))
    )
    results = db.session.scalars(query).all()
    query = str(query).replace("\n", "")
    return results

@app.route(rule="/delete")
def deleted():
    return jsonify(deleted=getDeleted(-1))

def validate_class_string(classStr:str):
    if classStr == "ha":
        return HomeworkRoom, HomeworkRoomAudit
    elif classStr == "emp":
        return Employee, EmployeeAudit
    else:
        abort(404)

@app.route(rule="/delete/<string:classStr>/<int:x>")
def delete(classStr:str, x:int):
    c, cAudit = validate_class_string(classStr)
    toDelete = db.session.get(c, x)
    if not isinstance(toDelete, c): return jsonify(msg="object to delete does not exist or is already deleted"), 404
    db.session.delete(toDelete)
    db.session.commit()
    return jsonify(msg="success")

@app.route(rule="/resurect/<string:classStr>/<int:x>")
def resurect(classStr:str, x:int):
    c, cAudit = validate_class_string(classStr)
    result = db.session.scalar(db.select(
        cAudit
    )
    .where(
        cAudit.id == x
    )
    .order_by(
        cAudit.audit_id.desc()
    ).limit(1))
    if not isinstance(result, cAudit) or not isinstance(result.audit_action, AuditAction) or result.audit_action != AuditAction.DELETE:
        return jsonify(msg="seems like the Employee is currently not deleted"), 500
    d = result.to_dict(keepData=True)
    id = d["id"]
    del(d["audit_id"], d["audit_action"], d["audit_datetime"], d["audit_issuer_id"], d["id"])
    if c == Employee:
        del(d["password_change_recomended"])
        resurected = c(**d, password=bcrypt.hashpw(bytes(Secrets.first_time_password, "UTF-8"), bcrypt.gensalt()), password_change_recomended=True)
    else:
        resurected = c(**d)

    resurected.id = id

    db.session.add(resurected)
    
    db.session.commit()
    return jsonify(msg="success", resurected=resurected.to_dict())

@app.route(rule="/test")
def test():
    t2 = aliased(HomeworkRoomAudit, name="t2")

    query = (
        db.select(
            db.func.max(t2.audit_id).label("id_latest"),
            HomeworkRoom,
            HomeworkRoomAudit
        )
        .where(
            HomeworkRoomAudit.id == HomeworkRoom.id & HomeworkRoomAudit.audit_id == t2.c.id_latest
        )
        .group_by(HomeworkRoom.id)
    )
    result = db.session.execute(query)
    print(result.fetchall())
    return jsonify(query=str(query))

if __name__ == "__main__":
    socketio.run(app, host = Secrets.server_host_v1, port = Secrets.server_port_v1, debug = True)#, ssl_context=('certificate/server.crt', 'certificate/private.key'))#, use_reloader=False)