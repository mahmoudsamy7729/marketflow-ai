"""add campaign cadence and content plans

Revision ID: 0007_content_plans
Revises: 0006_add_posts_image_prompt
Create Date: 2026-03-31 02:30:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0007_content_plans"
down_revision = "0006_add_posts_image_prompt"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "campaigns",
        sa.Column("posts_per_interval", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column(
        "campaigns",
        sa.Column("interval_days", sa.Integer(), nullable=False, server_default="1"),
    )
    op.add_column("posts", sa.Column("content_plan_item_id", sa.Uuid(), nullable=True))
    op.create_index(op.f("ix_posts_content_plan_item_id"), "posts", ["content_plan_item_id"], unique=False)

    op.create_table(
        "content_plans",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("campaign_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
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
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_content_plans_campaign_id"), "content_plans", ["campaign_id"], unique=False)
    op.create_index(op.f("ix_content_plans_user_id"), "content_plans", ["user_id"], unique=False)
    op.create_index(op.f("ix_content_plans_status"), "content_plans", ["status"], unique=False)

    op.create_table(
        "content_plan_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("content_plan_id", sa.Uuid(), nullable=False),
        sa.Column("campaign_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("channel", sa.String(length=50), nullable=False),
        sa.Column("sequence_order", sa.Integer(), nullable=False),
        sa.Column("day_number", sa.Integer(), nullable=False),
        sa.Column("planned_for", sa.Date(), nullable=False),
        sa.Column("content_type", sa.Text(), nullable=False),
        sa.Column("topic", sa.Text(), nullable=False),
        sa.Column("angle", sa.Text(), nullable=False),
        sa.Column("goal", sa.Text(), nullable=False),
        sa.Column("funnel_stage", sa.Text(), nullable=False),
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
        sa.ForeignKeyConstraint(["content_plan_id"], ["content_plans.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_content_plan_items_content_plan_id"), "content_plan_items", ["content_plan_id"], unique=False)
    op.create_index(op.f("ix_content_plan_items_campaign_id"), "content_plan_items", ["campaign_id"], unique=False)
    op.create_index(op.f("ix_content_plan_items_user_id"), "content_plan_items", ["user_id"], unique=False)
    op.create_index(op.f("ix_content_plan_items_channel"), "content_plan_items", ["channel"], unique=False)
    op.create_index(op.f("ix_content_plan_items_planned_for"), "content_plan_items", ["planned_for"], unique=False)
    op.create_index(op.f("ix_content_plan_items_status"), "content_plan_items", ["status"], unique=False)

    op.create_foreign_key(
        "fk_posts_content_plan_item_id_content_plan_items",
        "posts",
        "content_plan_items",
        ["content_plan_item_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_posts_content_plan_item_id_content_plan_items", "posts", type_="foreignkey")
    op.drop_index(op.f("ix_content_plan_items_status"), table_name="content_plan_items")
    op.drop_index(op.f("ix_content_plan_items_planned_for"), table_name="content_plan_items")
    op.drop_index(op.f("ix_content_plan_items_channel"), table_name="content_plan_items")
    op.drop_index(op.f("ix_content_plan_items_user_id"), table_name="content_plan_items")
    op.drop_index(op.f("ix_content_plan_items_campaign_id"), table_name="content_plan_items")
    op.drop_index(op.f("ix_content_plan_items_content_plan_id"), table_name="content_plan_items")
    op.drop_table("content_plan_items")
    op.drop_index(op.f("ix_content_plans_status"), table_name="content_plans")
    op.drop_index(op.f("ix_content_plans_user_id"), table_name="content_plans")
    op.drop_index(op.f("ix_content_plans_campaign_id"), table_name="content_plans")
    op.drop_table("content_plans")
    op.drop_index(op.f("ix_posts_content_plan_item_id"), table_name="posts")
    op.drop_column("posts", "content_plan_item_id")
    op.drop_column("campaigns", "interval_days")
    op.drop_column("campaigns", "posts_per_interval")
