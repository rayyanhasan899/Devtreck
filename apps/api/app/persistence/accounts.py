from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import case, delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.core.security import digest
from app.persistence.models import RateLimitModel, SessionModel, UserModel


class AccountsRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def by_email(self, email: str) -> UserModel | None:
        return self.session.scalar(select(UserModel).where(UserModel.email == email))

    def authenticated(self, token_hash: str) -> UserModel | None:
        return self.session.scalar(
            select(UserModel)
            .join(SessionModel)
            .where(
                SessionModel.token_hash == token_hash, SessionModel.expires_at > datetime.now(UTC)
            )
        )

    def lock(self, user_id: UUID) -> UserModel:
        return self.session.scalars(
            select(UserModel)
            .where(UserModel.id == user_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        ).one()

    def revoke(self, user_id: UUID) -> None:
        self.session.execute(delete(SessionModel).where(SessionModel.user_id == user_id))

    def logout(self, token_hash: str) -> None:
        self.session.execute(delete(SessionModel).where(SessionModel.token_hash == token_hash))

    def forget_email_limit(self, email: str) -> None:
        self.session.execute(
            delete(RateLimitModel).where(RateLimitModel.key == digest("login-email:" + email))
        )

    def throttle(self, key: str, window: int) -> int:
        self.session.execute(delete(RateLimitModel).where(RateLimitModel.window < window - 1))
        statement = insert(RateLimitModel).values(key=key, window=window, attempts=1)
        returning = statement.on_conflict_do_update(
            index_elements=[RateLimitModel.key],
            set_={
                "window": window,
                "attempts": case(
                    (RateLimitModel.window == window, RateLimitModel.attempts + 1), else_=1
                ),
            },
        ).returning(RateLimitModel.attempts)
        attempts = self.session.scalar(returning)
        self.session.commit()
        assert attempts is not None
        return attempts
