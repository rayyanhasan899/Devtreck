from alembic import context
from sqlalchemy import create_engine, pool

from app.core.config import Settings
from app.database.base import Base
from app.persistence import models  # noqa: F401

settings = Settings()
if settings.database_url is None:
    raise RuntimeError("DATABASE_URL must be configured")
url = settings.database_url.get_secret_value()
if context.is_offline_mode():
    context.configure(url=url, target_metadata=Base.metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = create_engine(url, poolclass=pool.NullPool, hide_parameters=True)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()
