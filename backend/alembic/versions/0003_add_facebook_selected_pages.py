"""add facebook selected pages

Revision ID: 0003_add_facebook_selected_pages
Revises: 0002_add_channels
Create Date: 2026-03-30 01:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0003_add_facebook_selected_pages"
down_revision = "0002_add_channels"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "facebook_selected_pages",
        sa.Column("connection_id", sa.Uuid(), nullable=False),
        sa.Column("facebook_page_id", sa.String(length=255), nullable=False),
        sa.Column("page_name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=255), nullable=True),
        sa.Column("page_access_token", sa.Text(), nullable=False),
        sa.Column("tasks", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["connection_id"],
            ["channel_connections.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("connection_id"),
    )
    op.create_index(
        op.f("ix_facebook_selected_pages_facebook_page_id"),
        "facebook_selected_pages",
        ["facebook_page_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_facebook_selected_pages_facebook_page_id"),
        table_name="facebook_selected_pages",
    )
    op.drop_table("facebook_selected_pages")
