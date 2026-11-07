from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.users import User
from app.persistence.models import UserModel


class SqlUserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, user_id: UUID) -> User | None:
        row = self.session.get(UserModel, user_id)
        return None if row is None else User(row.id, row.email, row.name)


class SqlUnitOfWork:
    """Caller owns the session; explicit commit, rollback on failed commit."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = SqlUserRepository(session)

    def commit(self) -> None:
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def rollback(self) -> None:
        self.session.rollback()
