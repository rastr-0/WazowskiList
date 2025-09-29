# password hashing
from passlib.context import CryptContext
# time
from datetime import datetime, timedelta

myctx = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_hashed_password(password: str) -> str:
    return myctx.hash(password)


def set_reminding_time(deadline: datetime) -> datetime:
    if deadline.time().hour == 0 and deadline.time().minute == 0:
        return deadline
    else:
        return deadline - timedelta(hours=1)
