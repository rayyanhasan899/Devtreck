import hashlib
import secrets
from threading import BoundedSemaphore

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.domain.errors import UnavailableError

hasher = PasswordHasher()
DUMMY_HASH = hasher.hash(secrets.token_urlsafe(32))
password_slots = BoundedSemaphore(2)


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def verify(encoded: str, password: str) -> bool:
    if not password_slots.acquire(blocking=False):
        raise UnavailableError()
    try:
        return hasher.verify(encoded, password)
    except VerificationError, InvalidHashError:
        return False
    finally:
        password_slots.release()


def hash_password(password: str) -> str:
    if not password_slots.acquire(blocking=False):
        raise UnavailableError()
    try:
        return hasher.hash(password)
    finally:
        password_slots.release()
