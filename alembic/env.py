from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.config import settings
from app.models import Base


config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    # offline режим без реального коннекта — строка ок
    url_str = str(settings.sqlalchemy_url_obj())
    context.configure(
        url=url_str,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # online режим: создаём engine напрямую, НЕ engine_from_config
    connectable = create_engine(
        settings.sqlalchemy_url_obj(),   # URL object (не строка)
        poolclass=pool.NullPool,
        future=True,
        # В редких случаях можно добавить:
        # connect_args={"options": "-c client_encoding=UTF8"},
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
