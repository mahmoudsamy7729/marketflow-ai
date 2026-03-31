"""add campaigns tables

Revision ID: 0004_add_campaigns_tables
Revises: 0003_add_facebook_selected_pages
Create Date: 2026-03-30 03:30:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0004_add_campaigns_tables"
down_revision = "0003_add_facebook_selected_pages"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "campaigns",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("goal", sa.Text(), nullable=False),
        sa.Column("hook_style", sa.Text(), nullable=False),
        sa.Column("tone", sa.Text(), nullable=False),
        sa.Column("target_audience", sa.Text(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_campaigns_status"), "campaigns", ["status"], unique=False)
    op.create_index(op.f("ix_campaigns_user_id"), "campaigns", ["user_id"], unique=False)

    op.create_table(
        "campaign_target_channels",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("campaign_id", sa.Uuid(), nullable=False),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "campaign_id",
            "channel",
            name="uq_campaign_target_channels_campaign_id_channel",
        ),
    )
    op.create_index(
        op.f("ix_campaign_target_channels_campaign_id"),
        "campaign_target_channels",
        ["campaign_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_campaign_target_channels_channel"),
        "campaign_target_channels",
        ["channel"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_campaign_target_channels_channel"),
        table_name="campaign_target_channels",
    )
    op.drop_index(
        op.f("ix_campaign_target_channels_campaign_id"),
        table_name="campaign_target_channels",
    )
    op.drop_table("campaign_target_channels")
    op.drop_index(op.f("ix_campaigns_user_id"), table_name="campaigns")
    op.drop_index(op.f("ix_campaigns_status"), table_name="campaigns")
    op.drop_table("campaigns")
