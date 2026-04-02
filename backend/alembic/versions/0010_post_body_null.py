"""make posts body nullable

Revision ID: 0010_post_body_null
Revises: 0009_fb_page_ig_cols
Create Date: 2026-04-02 15:30:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0010_post_body_null"
down_revision = "0009_fb_page_ig_cols"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "posts",
        "body",
        existing_type=sa.Text(),
        nullable=True,
    )


def downgrade() -> None:
    op.execute("UPDATE posts SET body = '' WHERE body IS NULL")
    op.alter_column(
        "posts",
        "body",
        existing_type=sa.Text(),
        nullable=False,
    )
