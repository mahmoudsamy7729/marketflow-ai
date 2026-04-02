from __future__ import annotations

from pathlib import Path

from src.channels import exceptions as channel_exceptions
from src.channels.providers import FacebookOAuthProvider
from src.config import BASE_DIR, settings
from src.posts.models import (
    REMOTE_URL_STORAGE_TYPE,
    UPLOADED_FILE_STORAGE_TYPE,
    Post,
    PostImage,
)


class FacebookPostPublisher:
    def __init__(self, facebook_provider: FacebookOAuthProvider) -> None:
        self.facebook_provider = facebook_provider

    async def publish(self, post: Post, selected_page) -> dict:
        if not post.images:
            return await self.facebook_provider.publish_feed_post(
                page_id=selected_page.facebook_page_id,
                page_access_token=selected_page.page_access_token,
                message=post.body or "",
            )

        media_ids: list[str] = []
        for image in sorted(post.images, key=lambda item: (item.sort_order, item.created_at)):
            media_ids.append(
                await self._upload_post_image(
                    image=image,
                    page_id=selected_page.facebook_page_id,
                    page_access_token=selected_page.page_access_token,
                )
            )

        return await self.facebook_provider.publish_feed_post_with_media(
            page_id=selected_page.facebook_page_id,
            page_access_token=selected_page.page_access_token,
            message=post.body or "",
            media_ids=media_ids,
        )

    async def _upload_post_image(
        self,
        *,
        image: PostImage,
        page_id: str,
        page_access_token: str,
    ) -> str:
        if image.storage_type == REMOTE_URL_STORAGE_TYPE:
            return await self.facebook_provider.upload_unpublished_photo_from_url(
                page_id=page_id,
                page_access_token=page_access_token,
                image_url=image.file_url,
            )

        if image.storage_type == UPLOADED_FILE_STORAGE_TYPE:
            if not image.file_path:
                raise channel_exceptions.FacebookPublishFailed()

            file_path = self._get_upload_root() / image.file_path
            try:
                file_bytes = file_path.read_bytes()
            except OSError as exc:
                raise channel_exceptions.FacebookPublishFailed() from exc

            return await self.facebook_provider.upload_unpublished_photo_from_bytes(
                page_id=page_id,
                page_access_token=page_access_token,
                file_bytes=file_bytes,
                filename=image.original_filename or file_path.name,
                mime_type=image.mime_type,
            )

        raise channel_exceptions.FacebookPublishFailed()

    def _get_upload_root(self) -> Path:
        configured_path = Path(settings.post_upload_dir)
        if configured_path.is_absolute():
            return configured_path
        return BASE_DIR / configured_path
