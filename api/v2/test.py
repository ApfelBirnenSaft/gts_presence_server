from sqlmodel import SQLModel, Field, BINARY
from typing import Optional
import datetime

class Employee(SQLModel, table=True):
    __versioned__ = {}

    #id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    username: str = Field(nullable=False, primary_key=True, max_length=64)

def db_column_name(c):
    print(dir(Employee.username))
    print(Employee.username)
    return f"{c.parent.class_.__tablename__}.{c}"

print(db_column_name(Employee.username))
"""import hmac
import hashlib

def calc_hmac(data: bytes, key: bytes) -> str:
    h = hmac.new(key, data, hashlib.sha256)
    return h.hexdigest()

# Beispiel
key = b'879f38fc142b7187e20cba552f658a638a785612'
data = bytes.fromhex('176c1bcc1b020ad65f1777fc37da68fd')

hmac_value = calc_hmac(data, key)
print("HMAC:", hmac_value)

# Später bei der Überprüfung
def verify_hmac(data: bytes, key: bytes, expected_hmac: str) -> bool:
    return hmac.compare_digest(calc_hmac(data, key), expected_hmac)"""
