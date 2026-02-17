"""seed roles

Revision ID: 0003_seed_roles
Revises: re0002_extensions_indexes

"""
from __future__ import annotations

from alembic import op

revision = "0003_seed_roles"
down_revision = "0002_extensions_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Фиксированные роли:
    # 1=user, 2=staff, 3=admin
    op.execute(
        """
        INSERT INTO roles (id, code, name)
        VALUES
          (1, 'user',  'User'),
          (2, 'staff', 'Staff'),
          (3, 'admin', 'Admin')
        ON CONFLICT (id) DO NOTHING;
        """
    )


def downgrade() -> None:
    # Вниз — удаляем только эти роли (аккуратно, если уже привязаны пользователи)
    # Для курсового обычно ок. Если боишься FK-конфликтов — можно не удалять.
    op.execute("DELETE FROM roles WHERE id IN (1,2,3);")
