# password hashing
from passlib.context import CryptContext
# dates
from datetime import datetime

myctx = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_hashed_password(password: str) -> str:
    return myctx.hash(password)


def make_date_humanitic(ugly_date: datetime) -> str:
    return ugly_date.strftime("%m/%d/%Y, %H:%M")
