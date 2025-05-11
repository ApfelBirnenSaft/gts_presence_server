from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import responses

from .student import *
from .employee import *
from .activity import *

from utils import BaseDBModelWithId

async def get_versions_dict(session: AsyncSession) -> dict[str, int]:
    classes: dict[str, type[BaseDBModelWithId]] = {
        "employee": Employee,
        "activity": Activity,
        "student": Student,
        "student_note": StudentNote,
        "student_absent_irregular": StudentAbsentIrregular,
        "student_absent_regular": StudentAbsentRegular,
        "student_activity_presence": StudentActivityPresence,}
    data = {}
    for name, cls in classes.items():
        if issubclass(cls, AppendOnlyDBModel):
            data[name] = await cls.get_current_version(session=session) or 0
        elif issubclass(cls, VersionedDBModel):
            data[name] = await cls.get_current_version(session=session) or 0
    
    return data
