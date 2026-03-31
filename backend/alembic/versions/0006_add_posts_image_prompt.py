"""add image_prompt to posts

Revision ID: 0006_add_posts_image_prompt
Revises: 0005_add_posts_tables
Create Date: 2026-03-30 07:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0006_add_posts_image_prompt"
down_revision = "0005_add_posts_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("posts", sa.Column("image_prompt", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("posts", "image_prompt")
