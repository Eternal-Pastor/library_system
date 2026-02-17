"""add FK constraints to link tables

Revision ID: 0004_add_fks_link_tables
Revises: 0003_seed_roles
"""
from __future__ import annotations

from alembic import op

revision = "0004_add_fks_link_tables"
down_revision = "0003_seed_roles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ---- user_roles ----
    op.create_foreign_key(
        "fk_user_roles_user_id_users",
        source_table="user_roles",
        referent_table="users",
        local_cols=["user_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_user_roles_role_id_roles",
        source_table="user_roles",
        referent_table="roles",
        local_cols=["role_id"],
        remote_cols=["id"],
        ondelete="RESTRICT",
    )

    # ---- user_groups ----
    op.create_foreign_key(
        "fk_user_groups_user_id_users",
        source_table="user_groups",
        referent_table="users",
        local_cols=["user_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_user_groups_group_id_groups",
        source_table="user_groups",
        referent_table="groups",
        local_cols=["group_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    # ---- user_groups ----
    op.drop_constraint("fk_user_groups_group_id_groups", "user_groups", type_="foreignkey")
    op.drop_constraint("fk_user_groups_user_id_users", "user_groups", type_="foreignkey")

    # ---- user_roles ----
    op.drop_constraint("fk_user_roles_role_id_roles", "user_roles", type_="foreignkey")
    op.drop_constraint("fk_user_roles_user_id_users", "user_roles", type_="foreignkey")
