from utils import BaseDBModelWithId
from typing import Optional
import datetime

class AppendOnlyDBModel(BaseDBModelWithId):
    def get_versions(self, last_version_id: int, only_till: Optional[datetime.date]) -> dict[str, str]:
        data = {}
        return data