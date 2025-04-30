from sqlmodel import Field
from typing import Optional
import enum

from api.database import VersionedDBModel

class ActivityType(enum.Enum):
    HomeworkRoom = "homework_room"
    SchoolClub = "school_club"

    @staticmethod
    def from_string(string):
        return {
            ActivityType.HomeworkRoom.value: ActivityType.HomeworkRoom,
            ActivityType.SchoolClub.value: ActivityType.SchoolClub,
            }[string]

    def __str__(self):
        return self.value

class Activity(VersionedDBModel, table=True):  
    activity_type: ActivityType = Field(nullable=False)
    
    short: str = Field(nullable=False, unique=True)
    title: str = Field(nullable=False)
    
    room_monday: Optional[str] = Field(nullable=True)
    room_tuesday: Optional[str]  = Field(nullable=True)
    room_wednesday: Optional[str]  = Field(nullable=True)
    room_thursday: Optional[str]  = Field(nullable=True)
