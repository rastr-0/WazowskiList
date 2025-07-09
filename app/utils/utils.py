# password hashing
from passlib.context import CryptContext

myctx = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_hashed_password(password: str) -> str:
    return myctx.hash(password)
