from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.campaigns.models import Campaign
from src.content_plans.models import ContentPlan, ContentPlanItem


class ContentPlanRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _campaign_statement(self):
        return select(Campaign).options(selectinload(Campaign.channels))

    def _plan_statement(self):
        return select(ContentPlan).options(selectinload(ContentPlan.items))

    async def get_campaign_by_id_for_user(self, campaign_id: UUID, user_id: UUID) -> Campaign | None:
        statement = self._campaign_statement().where(
            Campaign.id == campaign_id,
            Campaign.user_id == user_id,
            Campaign.deleted_at.is_(None),
        )
        return await self.session.scalar(statement)

    async def get_active_plan_by_campaign_for_user(
        self,
        campaign_id: UUID,
        user_id: UUID,
    ) -> ContentPlan | None:
        statement = self._plan_statement().where(
            ContentPlan.campaign_id == campaign_id,
            ContentPlan.user_id == user_id,
            ContentPlan.status == "active",
        )
        return await self.session.scalar(statement)

    async def archive_active_plan_for_campaign(self, campaign_id: UUID, user_id: UUID) -> None:
        plan = await self.get_active_plan_by_campaign_for_user(campaign_id, user_id)
        if plan is None:
            return
        plan.status = "archived"
        await self.session.commit()

    async def create_plan_with_items(
        self,
        *,
        user_id: UUID,
        campaign_id: UUID,
        items: list[dict[str, str | int | date]],
    ) -> ContentPlan:
        plan = ContentPlan(
            campaign_id=campaign_id,
            user_id=user_id,
            status="active",
            items=[
                ContentPlanItem(
                    campaign_id=campaign_id,
                    user_id=user_id,
                    channel=str(item["channel"]),
                    sequence_order=int(item["sequence_order"]),
                    day_number=int(item["day_number"]),
                    planned_for=item["planned_for"],
                    content_type=str(item["content_type"]),
                    topic=str(item["topic"]),
                    angle=str(item["angle"]),
                    goal=str(item["goal"]),
                    funnel_stage=str(item["funnel_stage"]),
                    status="planned",
                )
                for item in items
            ],
        )
        self.session.add(plan)
        await self.session.commit()
        statement = self._plan_statement().where(ContentPlan.id == plan.id)
        return await self.session.scalar(statement)

    async def get_plan_item_by_id_for_user(self, item_id: UUID, user_id: UUID) -> ContentPlanItem | None:
        statement = (
            select(ContentPlanItem)
            .join(ContentPlan, ContentPlan.id == ContentPlanItem.content_plan_id)
            .options(selectinload(ContentPlanItem.content_plan))
            .where(
                ContentPlanItem.id == item_id,
                ContentPlanItem.user_id == user_id,
            )
        )
        return await self.session.scalar(statement)

    async def update_plan_item(
        self,
        item: ContentPlanItem,
        *,
        planned_for: date | None,
        content_type: str | None,
        topic: str | None,
        angle: str | None,
        goal: str | None,
        funnel_stage: str | None,
        status: str | None,
        day_number: int | None,
    ) -> ContentPlanItem:
        if planned_for is not None:
            item.planned_for = planned_for
        if day_number is not None:
            item.day_number = day_number
        if content_type is not None:
            item.content_type = content_type
        if topic is not None:
            item.topic = topic
        if angle is not None:
            item.angle = angle
        if goal is not None:
            item.goal = goal
        if funnel_stage is not None:
            item.funnel_stage = funnel_stage
        if status is not None:
            item.status = status

        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def list_active_planned_items_by_campaign_for_user(
        self,
        campaign_id: UUID,
        user_id: UUID,
    ) -> list[ContentPlanItem]:
        statement = (
            select(ContentPlanItem)
            .join(ContentPlan, ContentPlan.id == ContentPlanItem.content_plan_id)
            .where(
                ContentPlanItem.campaign_id == campaign_id,
                ContentPlanItem.user_id == user_id,
                ContentPlan.status == "active",
                ContentPlanItem.status == "planned",
            )
            .order_by(ContentPlanItem.sequence_order.asc())
        )
        result = await self.session.scalars(statement)
        return list(result.all())
