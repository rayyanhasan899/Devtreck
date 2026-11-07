from collections.abc import Iterator

import certifi
from fastapi import Request
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


def build_engine(url: str) -> Engine:
    return create_engine(
        url,
        pool_pre_ping=True,
        hide_parameters=True,
        connect_args={
            "connect_timeout": 10,
            "options": "-c timezone=UTC",
            "sslrootcert": certifi.where(),
        },
        pool_size=5,
        max_overflow=5,
    )


def get_session(request: Request) -> Iterator[Session]:
    engine: Engine | None = request.app.state.engine
    if engine is None:
        from app.domain.errors import UnavailableError

        raise UnavailableError()
    with sessionmaker(engine, expire_on_commit=False)() as session:
        try:
            yield session
        finally:
            session.rollback()
