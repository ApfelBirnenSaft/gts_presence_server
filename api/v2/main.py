from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
import datetime

from ..models import *
from ..database import get_session

b = datetime.datetime.now(datetime.timezone.utc).isoformat()
print(b)
b = datetime.datetime.fromisoformat(b)
print(b.isoformat())
print(b.astimezone(datetime.timezone(datetime.timedelta(hours=2))))

router = APIRouter()

@router.post("/users", response_model=User)
def create_user(user: User, session: Session = Depends(get_session)):
    user.created = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2)))
    print(user.created.isoformat())
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.get("/users", response_model=list[User])
def read_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()

class LoginRequest(BaseModel):
    username: str
    password: str
class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    user_id: int
@router.post('/login', response_model=LoginResponse)
def login(data: LoginRequest):
    user = None
    for user_id, user_data in users_db.items():
        if user_data["username"] == data.username:
            if user_data["password"] == data.password:
                return LoginResponse(access_token="", refresh_token="", user_id=user_id)
            else:
                return HTTPException(401)
    return HTTPException(404)

"""
@app.route('/refresh', methods=['GET'])
@jwt_required(refresh=True)
def refresh():
    return jsonify(access_token=new_access_token, user=user.to_dict(password_change_recomended_null=False)), 200

@app.route(rule="/trigger_data_refresh", methods = ["GET"])
@jwt_required()
@min_sec_lvl_required(3)
def trigger_data_refresh():
    return jsonify(msg="success")

@app.route(rule="/load_data/<string:current_version_datetime>", methods = ["GET"])
@jwt_required()
@min_sec_lvl_required(0)
def load_data(current_version_datetime:str):
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
    return jsonify(msg="success")

@app.route(rule="/student_presence", methods = ["POST"])
@jwt_required()
@min_sec_lvl_required(1)
def post_student_presence():
    return jsonify(msg="success")

@app.route(rule="/add_student_absence_regular", methods = ["POST"])
@jwt_required()
@min_sec_lvl_required(3)
def post_student_absence_regular():
    return jsonify(msg="success")

@app.route(rule="/delete_student_absence_regular", methods = ["POST"])
@jwt_required()
@min_sec_lvl_required(3)
def delete_student_absence_regular():
    return jsonify(msg="success")

@app.route(rule="/add_student_absence_irregular", methods = ["POST"])
@jwt_required()
@min_sec_lvl_required(3)
def post_student_absence_irregular():
    return jsonify(msg="success")

@app.route(rule="/delete_student_absence_irregular", methods = ["POST"])
@jwt_required()
@min_sec_lvl_required(3)
def delete_student_absence_irregular():
    return jsonify(msg="success")


@app.route(rule="/change_password", methods = ["POST"])
@jwt_required()
@min_sec_lvl_required(0)
def change_password():
    return jsonify(msg="success")


@app.route(rule="/reset_password", methods = ["POST"])
@jwt_required()
@min_sec_lvl_required(2)
def reset_password():
    return jsonify(msg="success", initPw=initPw)

'''
@app.route(rule="/fRs", methods = ["GET"])
def get_feature_requests():
    fRs = FeatureRequest.query.filter(FeatureRequest.parent_id == None).all()
    return [fRs[i].to_dict() for i in range(len(fRs))]
'''

@app.route(rule="/delete_student_note", methods = ["POST"])
@jwt_required()
@min_sec_lvl_required(1)
def delete_student_note():
    return jsonify(msg="success")

@app.route(rule="/update_student_note", methods = ["POST"])
@jwt_required()
@min_sec_lvl_required(1)
def update_student_note():
    return jsonify(msg="success")

@app.route(rule="/update_student", methods = ["POST"])
@jwt_required()
@min_sec_lvl_required(3)
def update_student():
    return jsonify(msg="success")
"""