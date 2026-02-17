"""extensions and indexes

Revision ID: 0002_extensions_indexes
Revises: f49eabedfcc9
Create Date: 2026-02-17
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# !!! ВАЖНО:
# 1) Заменить Revises на id предыдущей миграции.
# 2) Revision ID можешь оставить авто-сгенерированный, этот текст не обязателен.

revision = "0002_extensions_indexes"
down_revision = "f49eabedfcc9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ---------- Extensions ----------
    # pgcrypto для gen_random_uuid(), pg_trgm для подсказок/похожести, unaccent опционально
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")

    # ---------- Trigram indexes ----------
    # authors.full_name
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_authors_full_name_trgm "
        "ON authors USING gin (full_name gin_trgm_ops);"
    )
    # book_cards.title
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_book_cards_title_trgm "
        "ON book_cards USING gin (title gin_trgm_ops);"
    )
    # (опционально) description trigram, тяжеловато — включай при необходимости
    # op.execute(
    #     "CREATE INDEX IF NOT EXISTS ix_book_cards_description_trgm "
    #     "ON book_cards USING gin (description gin_trgm_ops);"
    # )

    # ---------- Standard indexes ----------
    # book_cards(book_id, status)
    op.create_index(
        "ix_book_cards_book_status",
        "book_cards",
        ["book_id", "status"],
        unique=False,
    )

    # book_copies indexes
    op.create_index("ix_book_copies_book_id", "book_copies", ["book_id"], unique=False)
    op.create_index("ix_book_copies_status", "book_copies", ["status"], unique=False)
    op.create_index("ix_book_copies_location", "book_copies", ["location_id"], unique=False)

    # reservations indexes
    op.create_index("ix_reservations_user_status", "reservations", ["user_id", "status"], unique=False)
    op.create_index("ix_reservations_book_status", "reservations", ["book_id", "status"], unique=False)
    op.create_index("ix_reservations_copy_status", "reservations", ["copy_id", "status"], unique=False)

    # notifications indexes
    # created_at DESC в Alembic удобно сделать raw SQL, иначе пляски с postgresql_ops
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_notifications_user_read_created "
        "ON notifications (user_id, is_read, created_at DESC);"
    )

    # loans indexes
    op.create_index("ix_loans_user_status", "loans", ["user_id", "status"], unique=False)
    op.create_index("ix_loans_copy_status", "loans", ["copy_id", "status"], unique=False)
    op.create_index("ix_loans_due_at", "loans", ["due_at"], unique=False)

    # similarities indexes
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_book_similarities_book_score "
        "ON book_similarities (book_id, score DESC);"
    )
    op.create_index("ix_book_similarities_model", "book_similarities", ["model_version"], unique=False)

    # audit indexes
    op.create_index("ix_audit_entity", "audit_log", ["entity_type", "entity_id"], unique=False)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_audit_actor_created "
        "ON audit_log (actor_user_id, created_at DESC);"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_audit_meta_gin "
        "ON audit_log USING gin (meta);"
    )

    # ---------- Partial unique indexes ----------
    # 1 активная заявка на книгу у пользователя (requested/approved)
    op.create_index(
        "uq_reservations_user_book_active",
        "reservations",
        ["user_id", "book_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('requested','approved')"),
    )

    # 1 открытая выдача на экземпляр (open/overdue)
    op.create_index(
        "uq_loans_copy_open",
        "loans",
        ["copy_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('open','overdue')"),
    )


def downgrade() -> None:
    # Индексы (обратный порядок, чтобы не споткнуться)
    op.drop_index("uq_loans_copy_open", table_name="loans")
    op.drop_index("uq_reservations_user_book_active", table_name="reservations")

    # audit
    op.execute("DROP INDEX IF EXISTS ix_audit_meta_gin;")
    op.execute("DROP INDEX IF EXISTS ix_audit_actor_created;")
    op.drop_index("ix_audit_entity", table_name="audit_log")

    # similarities
    op.drop_index("ix_book_similarities_model", table_name="book_similarities")
    op.execute("DROP INDEX IF EXISTS ix_book_similarities_book_score;")

    # loans
    op.drop_index("ix_loans_due_at", table_name="loans")
    op.drop_index("ix_loans_copy_status", table_name="loans")
    op.drop_index("ix_loans_user_status", table_name="loans")

    # notifications
    op.execute("DROP INDEX IF EXISTS ix_notifications_user_read_created;")

    # reservations
    op.drop_index("ix_reservations_copy_status", table_name="reservations")
    op.drop_index("ix_reservations_book_status", table_name="reservations")
    op.drop_index("ix_reservations_user_status", table_name="reservations")

    # book_copies
    op.drop_index("ix_book_copies_location", table_name="book_copies")
    op.drop_index("ix_book_copies_status", table_name="book_copies")
    op.drop_index("ix_book_copies_book_id", table_name="book_copies")

    # book_cards
    op.drop_index("ix_book_cards_book_status", table_name="book_cards")

    # trigram
    op.execute("DROP INDEX IF EXISTS ix_book_cards_title_trgm;")
    op.execute("DROP INDEX IF EXISTS ix_authors_full_name_trgm;")

    # extensions (обычно не удаляют в downgrade; но если нужно — раскомментируй)
    # op.execute("DROP EXTENSION IF EXISTS unaccent;")
    # op.execute("DROP EXTENSION IF EXISTS pg_trgm;")
    # op.execute("DROP EXTENSION IF EXISTS pgcrypto;")
