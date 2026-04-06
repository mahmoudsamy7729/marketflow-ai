"""add ai settings and admin support

Revision ID: 0012_ai_settings_and_admin
Revises: 0011_media_jobs
Create Date: 2026-04-06 12:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0012_ai_settings_and_admin"
down_revision = "0011_media_jobs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )

    op.create_table(
        "ai_provider_configs",
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("base_url", sa.String(length=500), nullable=False),
        sa.Column("model", sa.String(length=255), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("provider"),
    )

    op.create_table(
        "user_ai_settings",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("encrypted_api_key", sa.Text(), nullable=True),
        sa.Column("api_key_last4", sa.String(length=4), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_index(op.f("ix_user_ai_settings_provider"), "user_ai_settings", ["provider"], unique=False)

    op.execute(
        """
        UPDATE users
        SET is_admin = true
        WHERE id = (
            SELECT id
            FROM users
            WHERE deleted_at IS NULL
            ORDER BY created_at ASC, email ASC
            LIMIT 1
        )
        AND NOT EXISTS (
            SELECT 1 FROM users WHERE deleted_at IS NULL AND is_admin = true
        )
        """
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_user_ai_settings_provider"), table_name="user_ai_settings")
    op.drop_table("user_ai_settings")
    op.drop_table("ai_provider_configs")
    op.drop_column("users", "is_admin")
