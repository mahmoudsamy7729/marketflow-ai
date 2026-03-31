from __future__ import annotations

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


ALLOWED_CONTENT_PLAN_STATUSES = ("active", "archived")
ALLOWED_CONTENT_PLAN_ITEM_STATUSES = ("planned", "post_generated", "skipped")
ALLOWED_CONTENT_PLAN_ITEM_TYPES = ("image", "video")


class ContentPlan(Base):
    __tablename__ = "content_plans"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    campaign_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    items: Mapped[list["ContentPlanItem"]] = relationship(
        back_populates="content_plan",
        cascade="all, delete-orphan",
        order_by="ContentPlanItem.sequence_order.asc()",
    )


class ContentPlanItem(Base):
    __tablename__ = "content_plan_items"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    content_plan_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("content_plans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    campaign_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    channel: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)
    planned_for: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    content_type: Mapped[str] = mapped_column(Text, nullable=False)
    topic: Mapped[str] = mapped_column(Text, nullable=False)
    angle: Mapped[str] = mapped_column(Text, nullable=False)
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    funnel_stage: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="planned", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    content_plan: Mapped[ContentPlan] = relationship(back_populates="items")
