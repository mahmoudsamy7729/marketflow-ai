from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from openai import AsyncOpenAI
from pydantic import BaseModel, Field, ValidationError

from src.auth.models import User
from src.campaigns import exceptions as campaign_exceptions
from src.content_plans import exceptions as content_plan_exceptions
from src.content_plans.constants import POST_FROM_PLAN_SYSTEM_PROMPT
from src.content_plans.repositories import ContentPlanRepository
from src.content_plans.schemas import GeneratePostsFromPlanResponse
from src.posts import exceptions
from src.posts.models import ALLOWED_POST_CHANNELS
from src.posts.repositories import PostRepository
from src.posts.services.post_service import PostService


class GeneratedPostFromPlanItem(BaseModel):
    content_plan_item_id: UUID
    body: str = Field(min_length=1)
    image_prompt: str | None = None


class GeneratedPostsFromPlanPayload(BaseModel):
    items: list[GeneratedPostFromPlanItem]


class PostGenerationService:
    def __init__(
        self,
        post_repository: PostRepository,
        content_plan_repository: ContentPlanRepository,
        client: AsyncOpenAI,
        model_name: str,
    ) -> None:
        self.post_repository = post_repository
        self.content_plan_repository = content_plan_repository
        self.client = client
        self.model_name = model_name
        self.post_service = PostService(post_repository)

    async def generate_posts_from_plan(
        self,
        user: User,
        campaign_id: UUID,
    ) -> GeneratePostsFromPlanResponse:
        campaign = await self.post_repository.get_campaign_by_id_for_user(campaign_id, user.id)
        if campaign is None:
            raise campaign_exceptions.CampaignNotFound()

        plan = await self.content_plan_repository.get_active_plan_by_campaign_for_user(campaign_id, user.id)
        if plan is None:
            raise content_plan_exceptions.ContentPlanNotFound()

        items = await self.content_plan_repository.list_active_planned_items_by_campaign_for_user(campaign_id, user.id)
        if not items:
            return GeneratePostsFromPlanResponse(campaign_id=campaign_id, posts_created=0, posts=[])

        generated_payload = await self._generate_posts_payload(campaign, items)
        validated_posts = self._validate_generated_posts(items, generated_payload)
        created_posts = await self.post_repository.bulk_create_posts_from_plan_items(
            user_id=user.id,
            campaign_id=campaign_id,
            generated_posts=validated_posts,
        )
        return GeneratePostsFromPlanResponse(
            campaign_id=campaign_id,
            posts_created=len(created_posts),
            posts=[self.post_service._to_response(post) for post in created_posts],
        )

    async def _generate_posts_payload(self, campaign: Any, items: list[Any]) -> GeneratedPostsFromPlanPayload:
        prompt_items = [
            {
                "content_plan_item_id": str(item.id),
                "channel": item.channel,
                "planned_for": str(item.planned_for),
                "content_type": item.content_type,
                "topic": item.topic,
                "angle": item.angle,
                "goal": item.goal,
                "funnel_stage": item.funnel_stage,
            }
            for item in items
        ]
        user_prompt = (
            f"Campaign Name: {campaign.name}\n"
            f"Campaign Goal: {campaign.goal}\n"
            f"Tone: {campaign.tone}\n"
            f"Hook Style: {campaign.hook_style}\n"
            f"Target Audience: {campaign.target_audience}\n"
            f"Notes: {campaign.notes or 'None'}\n"
            f"Plan Items JSON:\n{json.dumps(prompt_items, ensure_ascii=False)}"
        )
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": POST_FROM_PLAN_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
            )
        except Exception as exc:
            raise exceptions.PostsGenerationFailed() from exc

        try:
            content = response.choices[0].message.content or "{}"
            parsed_content = json.loads(content)
            return GeneratedPostsFromPlanPayload.model_validate(parsed_content)
        except (AttributeError, IndexError, TypeError, json.JSONDecodeError, ValidationError) as exc:
            raise exceptions.PostsGenerationInvalidOutput() from exc

    def _validate_generated_posts(
        self,
        items: list[Any],
        generated_payload: GeneratedPostsFromPlanPayload,
    ) -> list[dict[str, str | UUID | None]]:
        item_map = {item.id: item for item in items}
        if len(generated_payload.items) != len(items):
            raise exceptions.PostsGenerationInvalidOutput()

        validated_posts: list[dict[str, str | UUID | None]] = []
        seen_ids: set[UUID] = set()
        for generated_item in generated_payload.items:
            plan_item = item_map.get(generated_item.content_plan_item_id)
            if plan_item is None or generated_item.content_plan_item_id in seen_ids:
                raise exceptions.PostsGenerationInvalidOutput()
            seen_ids.add(generated_item.content_plan_item_id)

            if plan_item.channel not in ALLOWED_POST_CHANNELS:
                raise exceptions.PostsGenerationInvalidOutput()

            body = generated_item.body.strip()
            if not body:
                raise exceptions.PostsGenerationInvalidOutput()

            image_prompt = generated_item.image_prompt.strip() if generated_item.image_prompt else None
            validated_posts.append(
                {
                    "content_plan_item_id": plan_item.id,
                    "channel": plan_item.channel,
                    "body": body,
                    "image_prompt": image_prompt,
                }
            )

        if len(seen_ids) != len(items):
            raise exceptions.PostsGenerationInvalidOutput()
        return validated_posts
