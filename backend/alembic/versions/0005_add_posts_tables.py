"""add posts tables

Revision ID: 0005_add_posts_tables
Revises: 0004_add_campaigns_tables
Create Date: 2026-03-30 05:15:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0005_add_posts_tables"
down_revision = "0004_add_campaigns_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "posts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("campaign_id", sa.Uuid(), nullable=False),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("external_post_id", sa.String(length=255), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
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
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_posts_campaign_id"), "posts", ["campaign_id"], unique=False)
    op.create_index(op.f("ix_posts_channel"), "posts", ["channel"], unique=False)
    op.create_index(op.f("ix_posts_status"), "posts", ["status"], unique=False)
    op.create_index(op.f("ix_posts_user_id"), "posts", ["user_id"], unique=False)

    op.create_table(
        "post_images",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("post_id", sa.Uuid(), nullable=False),
        sa.Column("storage_type", sa.String(length=50), nullable=False),
        sa.Column("file_url", sa.Text(), nullable=False),
        sa.Column("file_path", sa.Text(), nullable=True),
        sa.Column("original_filename", sa.String(length=255), nullable=True),
        sa.Column("mime_type", sa.String(length=255), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_post_images_post_id"), "post_images", ["post_id"], unique=False)
    op.create_index(op.f("ix_post_images_storage_type"), "post_images", ["storage_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_post_images_storage_type"), table_name="post_images")
    op.drop_index(op.f("ix_post_images_post_id"), table_name="post_images")
    op.drop_table("post_images")
    op.drop_index(op.f("ix_posts_user_id"), table_name="posts")
    op.drop_index(op.f("ix_posts_status"), table_name="posts")
    op.drop_index(op.f("ix_posts_channel"), table_name="posts")
    op.drop_index(op.f("ix_posts_campaign_id"), table_name="posts")
    op.drop_table("posts")
