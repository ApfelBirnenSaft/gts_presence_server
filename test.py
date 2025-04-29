import pydantic
from api.database import async_session, create_all_tables
import api.models as models
import asyncio
from copy import copy

async def create():
    async with async_session() as session:
        await create_all_tables()
        #session.add(models.Activity(activity_type=models.ActivityType.HomeworkRoom, short="235", title="230", room_monday=None, room_tuesday=None, room_wednesday=None, room_thursday=None))
        #session.add(models.Student(first_name="Alexander", last_name="Steinbrück", grade=11, class_id="EK1", monday_homework_room_id=1, tuesday_homework_room_id=1, wednesday_homework_room_id=1, thursday_homework_room_id=1, monday_school_club_id=1, tuesday_school_club_id=1, wednesday_school_club_id=1, thursday_school_club_id=1))
        #(await session.get_one(models.Activity, 1)).title = "241"
        
        await session.commit()

if __name__ == "__main__":
    asyncio.run(create())