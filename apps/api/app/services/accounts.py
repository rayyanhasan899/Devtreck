import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import DUMMY_HASH, digest, hash_password, hasher, verify
from app.domain.errors import ConflictError, UnauthorizedError
from app.persistence.accounts import AccountsRepository
from app.persistence.models import SessionModel, UserModel
from app.persistence.unit_of_work import SqlUnitOfWork


class AccountsService:
    def __init__(self, session: Session) -> None:
        self.db = session
        self.repo = AccountsRepository(session)
        self.uow = SqlUnitOfWork(session)

    def commit(self) -> None:
        try:
            self.uow.commit()
        except IntegrityError:
            raise ConflictError() from None

    def register(self, name: str, email: str, password: str) -> UserModel:
        user = UserModel(name=name, email=email.lower(), password_hash=hash_password(password))
        self.db.add(user)
        self.commit()
        return user

    def login(self, email: str, password: str) -> tuple[UserModel, str]:
        user = self.repo.by_email(email.lower())
        if user is not None:
            user = self.repo.lock(user.id)
        valid = verify(user.password_hash if user else DUMMY_HASH, password)
        if user is None or not valid:
            raise UnauthorizedError()
        if hasher.check_needs_rehash(user.password_hash):
            user.password_hash = hash_password(password)
        token = secrets.token_urlsafe(32)
        self.db.add(
            SessionModel(
                user_id=user.id,
                token_hash=digest(token),
                expires_at=datetime.now(UTC) + timedelta(days=7),
            )
        )
        self.commit()
        return user, token

    def require(self, token: str | None) -> UserModel:
        if token is None or len(token) > 100:
            raise UnauthorizedError()
        user = self.repo.authenticated(digest(token))
        if user is None:
            raise UnauthorizedError()
        self.repo.lock(user.id)
        if self.repo.authenticated(digest(token)) is None:
            raise UnauthorizedError()
        return user

    def reauthenticate(self, user: UserModel, password: str | None) -> UserModel:
        locked = self.repo.lock(user.id)
        if not password or not verify(locked.password_hash, password):
            raise UnauthorizedError()
        return locked

    def update(self, user: UserModel, changes: dict[str, str], password: str | None) -> UserModel:
        locked = self.repo.lock(user.id)
        if "email" in changes:
            self.reauthenticate(locked, password)
            changes["email"] = changes["email"].lower()
            self.repo.revoke(locked.id)
        for key, value in changes.items():
            setattr(locked, key, value)
        self.commit()
        return locked

    def change_password(self, user: UserModel, current: str, new: str) -> None:
        locked = self.reauthenticate(user, current)
        locked.password_hash = hash_password(new)
        self.repo.revoke(locked.id)
        self.commit()

    def delete(self, user: UserModel, password: str) -> None:
        locked = self.reauthenticate(user, password)
        self.repo.forget_email_limit(locked.email)
        self.db.delete(locked)
        self.commit()

    def logout(self, token: str) -> None:
        self.repo.logout(digest(token))
        self.commit()
