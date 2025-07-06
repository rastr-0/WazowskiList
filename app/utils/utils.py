# password hashing
from passlib.context import CryptContext
# dates
from datetime import datetime

myctx = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_hashed_password(password: str) -> str:
    return myctx.hash(password)


def convert_to_optional(schema):
    from typing import Optional
    return {k: Optional[v] for k, v in schema.__annotations__.items()}


def make_date_humanitic(ugly_date: datetime) -> str:
    return ugly_date.strftime("%m/%d/%Y, %H:%M")
