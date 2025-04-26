import datetime
import re, string

def get_datetime_utc() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)

def camel_to_snake(s: str) -> str:
    result = re.sub(r'([A-Z])', r'_\1', s).lower()
    for c in s:
        if c != "_":
            if re.match(r'([A-Z])', c):
                result = result[1:]
            break
    return result

DB_ID_NOT_SET_EXCEPTION = ValueError("id is not set.")