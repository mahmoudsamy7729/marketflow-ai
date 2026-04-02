"""add media generation jobs

Revision ID: 0011_media_jobs
Revises: 0010_post_body_null
Create Date: 2026-04-02 17:10:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0011_media_jobs"
down_revision = "0010_post_body_null"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "media_generation_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("post_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("media_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("external_job_id", sa.String(length=255), nullable=True),
        sa.Column("result_url", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_media_generation_jobs_post_id"), "media_generation_jobs", ["post_id"], unique=False)
    op.create_index(op.f("ix_media_generation_jobs_user_id"), "media_generation_jobs", ["user_id"], unique=False)
    op.create_index(op.f("ix_media_generation_jobs_provider"), "media_generation_jobs", ["provider"], unique=False)
    op.create_index(op.f("ix_media_generation_jobs_media_type"), "media_generation_jobs", ["media_type"], unique=False)
    op.create_index(op.f("ix_media_generation_jobs_status"), "media_generation_jobs", ["status"], unique=False)
    op.create_index(op.f("ix_media_generation_jobs_external_job_id"), "media_generation_jobs", ["external_job_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_media_generation_jobs_external_job_id"), table_name="media_generation_jobs")
    op.drop_index(op.f("ix_media_generation_jobs_status"), table_name="media_generation_jobs")
    op.drop_index(op.f("ix_media_generation_jobs_media_type"), table_name="media_generation_jobs")
    op.drop_index(op.f("ix_media_generation_jobs_provider"), table_name="media_generation_jobs")
    op.drop_index(op.f("ix_media_generation_jobs_user_id"), table_name="media_generation_jobs")
    op.drop_index(op.f("ix_media_generation_jobs_post_id"), table_name="media_generation_jobs")
    op.drop_table("media_generation_jobs")
