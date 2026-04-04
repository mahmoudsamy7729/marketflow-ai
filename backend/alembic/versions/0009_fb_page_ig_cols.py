"""reconcile duplicate instagram columns revision

Revision ID: 0009_fb_page_ig_cols
Revises: 0008_instagram_tables
Create Date: 2026-04-02 14:10:00
"""
from __future__ import annotations

revision = "0009_fb_page_ig_cols"
down_revision = "0008_instagram_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Revision 0008 already added these columns and index. Keep 0009 as a
    # no-op so databases that failed on the duplicate ALTER TABLE can advance.
    pass


def downgrade() -> None:
    # Downgrading from 0009 to 0008 should not change schema because 0008
    # already owns the Instagram columns.
    pass
