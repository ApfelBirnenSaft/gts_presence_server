from sqlmodel import SQLModel, Field
from typing import Optional
import datetime, enum

from api.database import versioning

from utils import DB_ID_NOT_SET_EXCEPTION

class ActivityType(enum.Enum):
    HomeworkRoom = "homwqork_room"
    SchoolClub = "school_club"

    @staticmethod
    def from_string(string):
        return {
            ActivityType.HomeworkRoom.value: ActivityType.HomeworkRoom,
            ActivityType.SchoolClub.value: ActivityType.SchoolClub,
            }[string]

    def __str__(self):
        return self.value

class Activity(SQLModel, versioning.VersionedMixin, table=True):    
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    last_change: datetime.datetime = Field(nullable=False)

    activity_type: ActivityType = Field(nullable=False)
    
    short: str = Field(nullable=False, unique=True)
    title: str = Field(nullable=False)
    
    room_monday: str = Field(nullable=True)
    room_tuesday: str = Field(nullable=True)
    room_wednesday: str = Field(nullable=True)
    room_thursday: str = Field(nullable=True)

    @property
    def id_strict(self) -> int:
        if isinstance(self.id, int): return self.id
        else: raise DB_ID_NOT_SET_EXCEPTION
