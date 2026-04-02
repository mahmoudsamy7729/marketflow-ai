from __future__ import annotations

from src.posts import exceptions
from src.channels.providers import FacebookOAuthProvider
from src.posts.models import REMOTE_URL_STORAGE_TYPE, Post


class InstagramPostPublisher:
    def __init__(self, facebook_provider: FacebookOAuthProvider) -> None:
        self.facebook_provider = facebook_provider

    async def publish(self, post: Post, selected_page) -> dict:
        instagram_account_id = (selected_page.instagram_account_id or "").strip()
        if not instagram_account_id:
            raise exceptions.PostInstagramTargetNotConfigured()

        images = sorted(post.images, key=lambda item: (item.sort_order, item.created_at))
        if not images:
            raise exceptions.PostInstagramMediaRequired()
        if len(images) != 1:
            raise exceptions.PostInstagramMediaCountUnsupported(len(images))

        image = images[0]
        if image.storage_type != REMOTE_URL_STORAGE_TYPE:
            raise exceptions.PostInstagramMediaSourceUnsupported(image.storage_type)

        creation_id = await self.facebook_provider.create_instagram_image_container(
            ig_account_id=instagram_account_id,
            access_token=selected_page.page_access_token,
            image_url=image.file_url,
            caption=post.body or None,
        )
        return await self.facebook_provider.publish_instagram_media(
            ig_account_id=instagram_account_id,
            access_token=selected_page.page_access_token,
            creation_id=creation_id,
        )
