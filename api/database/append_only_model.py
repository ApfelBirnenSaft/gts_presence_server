from sqlmodel import Field, and_, func, select
from utils import BaseDBModelWithId
from typing import Optional
import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from utils import get_datetime_utc

class AppendOnlyDBModel(BaseDBModelWithId):
    date_time: datetime.datetime = Field(default_factory=get_datetime_utc)

    @classmethod
    async def get_current_version(cls, session: AsyncSession) -> Optional[int]:
        highest_version = (await session.execute(select(cls).order_by(getattr(cls.id, 'desc')()).limit(1))).scalar_one_or_none()
        return highest_version.id_strict if highest_version != None else None
    
    @classmethod
    async def get_new(cls, session: AsyncSession, last_version_id: int, only_till: Optional[datetime.date]) -> dict[str, str]:
        data = {}
        highest_version = (await session.execute(select(cls).order_by(getattr(cls.id, 'desc')()).limit(1))).scalar_one_or_none()
        if highest_version == None or highest_version.id_strict <= last_version_id:
            data.setdefault("version", {})["id"] = highest_version.id_strict if highest_version != None else 0
            data["version"]["date_time"] = highest_version.date_time.isoformat() if highest_version != None else None
            data.setdefault("deleted", [])
            data.setdefault("changed", [])
            return data
        
        conditions = [
            getattr(cls, "id") > last_version_id
        ]
        if only_till is not None:
            conditions.append(
                func.date(cls.date_time) <= only_till
            )
        query = (
            select(cls)
            .where(and_(*conditions))
            .order_by(getattr(cls, "id"))
        )
        new_entries = (await session.execute(query)).scalars()
        for entry in new_entries:
            data.setdefault("version", {})["id"] = entry.id
            data["version"]["date_time"] = entry.date_time.isoformat()
            data.setdefault("changed", []).append(entry.model_dump(mode="json"))
        return data