"""add instagram metadata to selected facebook pages

Revision ID: 0008_instagram_tables
Revises: 0007_content_plans
Create Date: 2026-04-02 12:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0008_instagram_tables"
down_revision = "0007_content_plans"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "facebook_selected_pages",
        sa.Column("instagram_account_id", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "facebook_selected_pages",
        sa.Column("instagram_username", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "facebook_selected_pages",
        sa.Column("instagram_name", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "facebook_selected_pages",
        sa.Column("instagram_profile_picture_url", sa.Text(), nullable=True),
    )
    op.create_index(
        op.f("ix_facebook_selected_pages_instagram_account_id"),
        "facebook_selected_pages",
        ["instagram_account_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_facebook_selected_pages_instagram_account_id"),
        table_name="facebook_selected_pages",
    )
    op.drop_column("facebook_selected_pages", "instagram_profile_picture_url")
    op.drop_column("facebook_selected_pages", "instagram_name")
    op.drop_column("facebook_selected_pages", "instagram_username")
    op.drop_column("facebook_selected_pages", "instagram_account_id")
