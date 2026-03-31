from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.campaigns.models import Campaign
from src.posts.models import Post, PostImage, REMOTE_URL_STORAGE_TYPE


class PostRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _post_statement(self):
        return select(Post).options(selectinload(Post.images))

    async def get_campaign_by_id_for_user(
        self,
        campaign_id: UUID,
        user_id: UUID,
    ) -> Campaign | None:
        statement = (
            select(Campaign)
            .options(selectinload(Campaign.channels))
            .where(
                Campaign.id == campaign_id,
                Campaign.user_id == user_id,
                Campaign.deleted_at.is_(None),
            )
        )
        return await self.session.scalar(statement)

    async def create_post(
        self,
        *,
        user_id: UUID,
        campaign_id: UUID,
        channel: str,
        body: str,
        status: str,
        scheduled_for: datetime | None,
        image_urls: list[str],
    ) -> Post:
        post = Post(
            user_id=user_id,
            campaign_id=campaign_id,
            channel=channel,
            body=body,
            status=status,
            scheduled_for=scheduled_for,
            images=[
                PostImage(
                    storage_type=REMOTE_URL_STORAGE_TYPE,
                    file_url=image_url,
                    sort_order=index,
                )
                for index, image_url in enumerate(image_urls, start=1)
            ],
        )
        self.session.add(post)
        await self.session.commit()
        return await self.get_post_by_id_for_user(post.id, user_id)

    async def list_posts_by_user(
        self,
        *,
        user_id: UUID,
        campaign_id: UUID | None,
        status: str | None,
        channel: str | None,
    ) -> list[Post]:
        statement = self._post_statement().where(
            Post.user_id == user_id,
            Post.deleted_at.is_(None),
        )
        if campaign_id is not None:
            statement = statement.where(Post.campaign_id == campaign_id)
        if status is not None:
            statement = statement.where(Post.status == status)
        if channel is not None:
            statement = statement.where(Post.channel == channel)

        statement = statement.order_by(Post.created_at.desc())
        result = await self.session.scalars(statement)
        return list(result.unique().all())

    async def get_post_by_id_for_user(
        self,
        post_id: UUID,
        user_id: UUID,
    ) -> Post | None:
        statement = self._post_statement().where(
            Post.id == post_id,
            Post.user_id == user_id,
            Post.deleted_at.is_(None),
        )
        return await self.session.scalar(statement)

    async def update_post(
        self,
        post: Post,
        *,
        body: str | None,
        update_body: bool,
        scheduled_for: datetime | None,
        update_scheduled_for: bool,
        status: str | None,
        update_status: bool,
        remote_image_urls: list[str] | None,
        replace_remote_image_urls: bool,
    ) -> Post:
        if update_body:
            post.body = body or post.body
        if update_scheduled_for:
            post.scheduled_for = scheduled_for
        if update_status:
            post.status = status or post.status

        if replace_remote_image_urls:
            existing_images = list(post.images)
            keep_images = [image for image in existing_images if image.storage_type != REMOTE_URL_STORAGE_TYPE]
            for image in existing_images:
                if image.storage_type == REMOTE_URL_STORAGE_TYPE:
                    await self.session.delete(image)

            next_sort_order = max((image.sort_order for image in keep_images), default=0) + 1
            for image_url in remote_image_urls or []:
                self.session.add(
                    PostImage(
                        post_id=post.id,
                        storage_type=REMOTE_URL_STORAGE_TYPE,
                        file_url=image_url,
                        sort_order=next_sort_order,
                    )
                )
                next_sort_order += 1

        await self.session.commit()
        return await self.get_post_by_id_for_user(post.id, post.user_id)

    async def soft_delete_post(self, post: Post) -> Post:
        post.deleted_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def append_post_images(
        self,
        post: Post,
        images: list[dict[str, str | None]],
    ) -> Post:
        next_sort_order = await self.get_next_image_sort_order(post.id)
        for image in images:
            self.session.add(
                PostImage(
                    post_id=post.id,
                    storage_type=str(image["storage_type"]),
                    file_url=str(image["file_url"]),
                    file_path=image.get("file_path"),
                    original_filename=image.get("original_filename"),
                    mime_type=image.get("mime_type"),
                    sort_order=next_sort_order,
                )
            )
            next_sort_order += 1

        await self.session.commit()
        return await self.get_post_by_id_for_user(post.id, post.user_id)

    async def get_post_image_for_post(
        self,
        post_id: UUID,
        image_id: UUID,
    ) -> PostImage | None:
        statement = select(PostImage).where(
            PostImage.post_id == post_id,
            PostImage.id == image_id,
        )
        return await self.session.scalar(statement)

    async def delete_post_image(self, image: PostImage) -> None:
        await self.session.delete(image)
        await self.session.commit()

    async def get_next_image_sort_order(self, post_id: UUID) -> int:
        statement = select(func.max(PostImage.sort_order)).where(PostImage.post_id == post_id)
        max_sort_order = await self.session.scalar(statement)
        return int(max_sort_order or 0) + 1
