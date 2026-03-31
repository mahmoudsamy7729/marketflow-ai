from __future__ import annotations

import json
from datetime import date, timedelta
from typing import Any
from uuid import UUID

from openai import AsyncOpenAI
from pydantic import BaseModel, Field, ValidationError

from src.auth.models import User
from src.campaigns import exceptions as campaign_exceptions
from src.content_plans import exceptions
from src.content_plans.constants import CONTENT_PLAN_SYSTEM_PROMPT
from src.content_plans.models import (
    ALLOWED_CONTENT_PLAN_ITEM_TYPES,
    ALLOWED_CONTENT_PLAN_ITEM_STATUSES,
    ContentPlan,
    ContentPlanItem,
)
from src.content_plans.repositories import ContentPlanRepository
from src.content_plans.schemas import ContentPlanItemResponse, ContentPlanResponse, UpdateContentPlanItemRequest


class GeneratedPlanItemOutput(BaseModel):
    slot_id: str
    content_type: str = Field(min_length=1)
    topic: str = Field(min_length=1)
    angle: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    funnel_stage: str = Field(min_length=1)


class GeneratedPlanPayload(BaseModel):
    items: list[GeneratedPlanItemOutput]


class ContentPlanService:
    def __init__(
        self,
        repository: ContentPlanRepository,
        client: AsyncOpenAI,
        model_name: str,
    ) -> None:
        self.repository = repository
        self.client = client
        self.model_name = model_name

    async def generate_plan(self, user: User, campaign_id: UUID) -> ContentPlanResponse:
        campaign = await self.repository.get_campaign_by_id_for_user(campaign_id, user.id)
        if campaign is None:
            raise campaign_exceptions.CampaignNotFound()

        if campaign.status == "draft":
            campaign.status = "active"

        slots = self._build_slots(campaign)
        generated_payload = await self._generate_plan_items(campaign, slots)
        items = self._merge_generated_items(slots, generated_payload)

        await self.repository.archive_active_plan_for_campaign(campaign.id, user.id)
        plan = await self.repository.create_plan_with_items(
            user_id=user.id,
            campaign_id=campaign.id,
            items=items,
        )
        return self._to_plan_response(plan)

    async def get_active_plan(self, user: User, campaign_id: UUID) -> ContentPlanResponse:
        campaign = await self.repository.get_campaign_by_id_for_user(campaign_id, user.id)
        if campaign is None:
            raise campaign_exceptions.CampaignNotFound()

        plan = await self.repository.get_active_plan_by_campaign_for_user(campaign_id, user.id)
        if plan is None:
            raise exceptions.ContentPlanNotFound()
        return self._to_plan_response(plan)

    async def update_plan_item(
        self,
        user: User,
        item_id: UUID,
        payload: UpdateContentPlanItemRequest,
    ) -> ContentPlanItemResponse:
        item = await self.repository.get_plan_item_by_id_for_user(item_id, user.id)
        if item is None:
            raise exceptions.ContentPlanItemNotFound()
        if item.content_plan.status != "active":
            raise exceptions.ContentPlanNotEditable()

        campaign = await self.repository.get_campaign_by_id_for_user(item.campaign_id, user.id)
        if campaign is None:
            raise campaign_exceptions.CampaignNotFound()

        normalized_status = None
        if payload.status is not None:
            normalized_status = self._normalize_item_status(payload.status)

        day_number = None
        if payload.planned_for is not None:
            if payload.planned_for < campaign.start_date or payload.planned_for > campaign.end_date:
                raise exceptions.ContentPlanItemDateInvalid()
            day_number = (payload.planned_for - campaign.start_date).days + 1

        updated_item = await self.repository.update_plan_item(
            item,
            planned_for=payload.planned_for,
            content_type=self._normalize_item_type(payload.content_type) if payload.content_type else None,
            topic=payload.topic.strip() if payload.topic else None,
            angle=payload.angle.strip() if payload.angle else None,
            goal=payload.goal.strip() if payload.goal else None,
            funnel_stage=payload.funnel_stage.strip() if payload.funnel_stage else None,
            status=normalized_status,
            day_number=day_number,
        )
        return self._to_item_response(updated_item)

    async def _generate_plan_items(self, campaign: Any, slots: list[dict[str, Any]]) -> GeneratedPlanPayload:
        user_prompt = self._build_generation_prompt(campaign, slots)
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": CONTENT_PLAN_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
            )
        except Exception as exc:
            raise exceptions.ContentPlanGenerationFailed() from exc

        try:
            content = response.choices[0].message.content or "{}"
            parsed_content = json.loads(content)
            return GeneratedPlanPayload.model_validate(parsed_content)
        except (AttributeError, IndexError, TypeError, json.JSONDecodeError, ValidationError) as exc:
            raise exceptions.ContentPlanGenerationInvalidOutput() from exc

    def _build_slots(self, campaign: Any) -> list[dict[str, Any]]:
        duration_days = (campaign.end_date - campaign.start_date).days + 1
        if duration_days <= 0:
            raise campaign_exceptions.CampaignDateRangeInvalid()

        slots: list[dict[str, Any]] = []
        interval_index = 0
        cursor = campaign.start_date
        while cursor <= campaign.end_date:
            interval_index += 1
            interval_end = min(cursor + timedelta(days=campaign.interval_days - 1), campaign.end_date)
            interval_length = (interval_end - cursor).days + 1
            offsets = self._distributed_offsets(campaign.posts_per_interval, interval_length)

            for channel_record in campaign.channels:
                for position, offset in enumerate(offsets, start=1):
                    planned_for = cursor + timedelta(days=offset)
                    slots.append(
                        {
                            "slot_id": f"{channel_record.channel}-{interval_index}-{position}",
                            "channel": channel_record.channel,
                            "planned_for": planned_for,
                            "day_number": (planned_for - campaign.start_date).days + 1,
                        }
                    )
            cursor = interval_end + timedelta(days=1)

        slots.sort(key=lambda item: (item["planned_for"], item["channel"], item["slot_id"]))
        for sequence_order, slot in enumerate(slots, start=1):
            slot["sequence_order"] = sequence_order
        return slots

    def _distributed_offsets(self, posts_per_interval: int, interval_length: int) -> list[int]:
        if interval_length <= 1:
            return [0] * posts_per_interval
        if posts_per_interval == 1:
            return [0]
        return [
            round(index * (interval_length - 1) / (posts_per_interval - 1))
            for index in range(posts_per_interval)
        ]

    def _merge_generated_items(
        self,
        slots: list[dict[str, Any]],
        generated_payload: GeneratedPlanPayload,
    ) -> list[dict[str, Any]]:
        slot_map = {slot["slot_id"]: slot for slot in slots}
        if len(generated_payload.items) != len(slots):
            raise exceptions.ContentPlanGenerationInvalidOutput()

        merged_items: list[dict[str, Any]] = []
        seen_slot_ids: set[str] = set()
        for generated_item in generated_payload.items:
            slot = slot_map.get(generated_item.slot_id)
            if slot is None or generated_item.slot_id in seen_slot_ids:
                raise exceptions.ContentPlanGenerationInvalidOutput()
            seen_slot_ids.add(generated_item.slot_id)
            normalized_content_type = self._normalize_item_type(generated_item.content_type)
            merged_items.append(
                {
                    "channel": slot["channel"],
                    "sequence_order": slot["sequence_order"],
                    "day_number": slot["day_number"],
                    "planned_for": slot["planned_for"],
                    "content_type": normalized_content_type,
                    "topic": generated_item.topic.strip(),
                    "angle": generated_item.angle.strip(),
                    "goal": generated_item.goal.strip(),
                    "funnel_stage": generated_item.funnel_stage.strip(),
                }
            )

        if len(seen_slot_ids) != len(slots):
            raise exceptions.ContentPlanGenerationInvalidOutput()
        return merged_items

    def _build_generation_prompt(self, campaign: Any, slots: list[dict[str, Any]]) -> str:
        slot_payload = [
            {
                "slot_id": slot["slot_id"],
                "channel": slot["channel"],
                "planned_for": str(slot["planned_for"]),
                "day_number": slot["day_number"],
                "sequence_order": slot["sequence_order"],
            }
            for slot in slots
        ]
        return (
            f"Campaign Details:\n"
            f"- Name: {campaign.name}\n"
            f"- Target Audience: {campaign.target_audience}\n"
            f"- Tone: {campaign.tone}\n"
            f"- Hook Style: {campaign.hook_style}\n"
            f"- Goal: {campaign.goal}\n"
            f"- Notes: {campaign.notes or 'None'}\n"
            f"- Start Date: {campaign.start_date}\n"
            f"- End Date: {campaign.end_date}\n"
            f"- Posts Per Interval: {campaign.posts_per_interval}\n"
            f"- Interval Days: {campaign.interval_days}\n"
            f"- Target Channels: {', '.join(channel.channel for channel in campaign.channels)}\n"
            f"Precomputed Publishing Slots (JSON):\n{json.dumps(slot_payload, ensure_ascii=False)}"
        )

    def _normalize_item_status(self, status: str) -> str:
        normalized = status.strip().lower()
        if normalized not in ALLOWED_CONTENT_PLAN_ITEM_STATUSES:
            raise exceptions.ContentPlanItemStatusInvalid(normalized)
        return normalized

    def _normalize_item_type(self, content_type: str) -> str:
        normalized = content_type.strip().lower()
        if normalized not in ALLOWED_CONTENT_PLAN_ITEM_TYPES:
            raise exceptions.ContentPlanItemTypeInvalid(normalized)
        return normalized

    def _to_plan_response(self, plan: ContentPlan) -> ContentPlanResponse:
        items = sorted(plan.items, key=lambda item: item.sequence_order)
        return ContentPlanResponse(
            id=plan.id,
            campaign_id=plan.campaign_id,
            user_id=plan.user_id,
            status=plan.status,
            items=[self._to_item_response(item) for item in items],
            created_at=plan.created_at,
            updated_at=plan.updated_at,
        )

    def _to_item_response(self, item: ContentPlanItem) -> ContentPlanItemResponse:
        return ContentPlanItemResponse(
            id=item.id,
            content_plan_id=item.content_plan_id,
            campaign_id=item.campaign_id,
            user_id=item.user_id,
            channel=item.channel,
            sequence_order=item.sequence_order,
            day_number=item.day_number,
            planned_for=item.planned_for,
            content_type=item.content_type,
            topic=item.topic,
            angle=item.angle,
            goal=item.goal,
            funnel_stage=item.funnel_stage,
            status=item.status,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
