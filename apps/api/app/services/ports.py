from typing import Protocol
from uuid import UUID

from app.domain.users import User


class UserRepository(Protocol):
    def get(self, user_id: UUID) -> User | None: ...


class UnitOfWork(Protocol):
    users: UserRepository

    def commit(self) -> None: ...
    def rollback(self) -> None: ...
