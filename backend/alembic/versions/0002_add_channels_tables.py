"""add channels tables

Revision ID: 0002_add_channels
Revises: 0001_create_users
Create Date: 2026-03-30 00:30:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0002_add_channels"
down_revision = "0001_create_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "channel_connections",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
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
    op.create_index(
        op.f("ix_channel_connections_provider"),
        "channel_connections",
        ["provider"],
        unique=False,
    )
    op.create_index(
        op.f("ix_channel_connections_user_id"),
        "channel_connections",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "facebook_connection_details",
        sa.Column("connection_id", sa.Uuid(), nullable=False),
        sa.Column("facebook_user_id", sa.String(length=255), nullable=False),
        sa.Column("access_token", sa.Text(), nullable=False),
        sa.Column("token_type", sa.String(length=50), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("granted_scopes", sa.Text(), nullable=True),
        sa.Column("display_name", sa.String(length=255), nullable=True),
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
        op.f("ix_facebook_connection_details_facebook_user_id"),
        "facebook_connection_details",
        ["facebook_user_id"],
        unique=False,
    )

    op.create_table(
        "oauth_states",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("state", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_oauth_states_provider"), "oauth_states", ["provider"], unique=False)
    op.create_index(op.f("ix_oauth_states_state"), "oauth_states", ["state"], unique=True)
    op.create_index(op.f("ix_oauth_states_user_id"), "oauth_states", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_oauth_states_user_id"), table_name="oauth_states")
    op.drop_index(op.f("ix_oauth_states_state"), table_name="oauth_states")
    op.drop_index(op.f("ix_oauth_states_provider"), table_name="oauth_states")
    op.drop_table("oauth_states")

    op.drop_index(
        op.f("ix_facebook_connection_details_facebook_user_id"),
        table_name="facebook_connection_details",
    )
    op.drop_table("facebook_connection_details")

    op.drop_index(op.f("ix_channel_connections_user_id"), table_name="channel_connections")
    op.drop_index(op.f("ix_channel_connections_provider"), table_name="channel_connections")
    op.drop_table("channel_connections")
