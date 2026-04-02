from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Mapping
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import UploadFile

from src.auth.models import User
from src.campaigns import exceptions as campaign_exceptions
from src.channels import exceptions as channel_exceptions
from src.channels.providers import FacebookOAuthProvider
from src.channels.repositories import ChannelRepository
from src.channels.repositories.channel_repository import FACEBOOK_PROVIDER, INSTAGRAM_PROVIDER
from src.common.exceptions import AppException
from src.config import BASE_DIR, settings
from src.posts import exceptions
from src.posts.models import (
    ALLOWED_POST_CHANNELS,
    ALLOWED_POST_STATUSES,
    EDITABLE_POST_STATUSES,
    REMOTE_URL_STORAGE_TYPE,
    UPLOADED_FILE_STORAGE_TYPE,
    Post,
    PostImage,
)
from src.posts.publishers import (
    FacebookPostPublisher,
    InstagramPostPublisher,
    PostPublisher,
)
from src.posts.repositories import PostRepository
from src.posts.schemas import (
    AttachImageUrlsRequest,
    PostCreateRequest,
    PostImageResponse,
    PostListResponse,
    PostMessageResponse,
    PostResponse,
    ScheduledPostsPublishResult,
    PostUpdateRequest,
)


class PostService:
    def __init__(
        self,
        repository: PostRepository,
        channel_repository: ChannelRepository | None = None,
        facebook_provider: FacebookOAuthProvider | None = None,
        publishers: Mapping[str, PostPublisher] | None = None,
    ) -> None:
        self.repository = repository
        self.channel_repository = channel_repository
        self.facebook_provider = facebook_provider
        self.publishers = dict(publishers or {})
        if not self.publishers and facebook_provider is not None:
            self.publishers = {
                FACEBOOK_PROVIDER: FacebookPostPublisher(facebook_provider),
                INSTAGRAM_PROVIDER: InstagramPostPublisher(facebook_provider),
            }

    async def create_post(self, user: User, payload: PostCreateRequest) -> PostResponse:
        campaign = await self.repository.get_campaign_by_id_for_user(payload.campaign_id, user.id)
        if campaign is None:
            raise exceptions.PostCampaignNotFound()

        channel = self._normalize_channel(payload.channel)
        self._ensure_channel_is_targeted(channel, campaign)

        scheduled_for = self._normalize_datetime(payload.scheduled_for, require_timezone=payload.scheduled_for is not None)
        if scheduled_for is not None:
            self._validate_schedule_for_campaign(campaign, payload.scheduled_for)
        status = "scheduled" if scheduled_for is not None else "draft"
        image_urls = [str(url) for url in payload.image_urls or []]

        post = await self.repository.create_post(
            user_id=user.id,
            campaign_id=campaign.id,
            content_plan_item_id=None,
            channel=channel,
            body=payload.body.strip() if payload.body else None,
            image_prompt=None,
            status=status,
            scheduled_for=scheduled_for,
            image_urls=image_urls,
        )
        return self._to_response(post)

    async def list_posts(
        self,
        user: User,
        *,
        campaign_id: UUID | None,
        status: str | None,
        channel: str | None,
    ) -> PostListResponse:
        normalized_status = self._normalize_status(status) if status is not None else None
        normalized_channel = self._normalize_channel(channel) if channel is not None else None

        posts = await self.repository.list_posts_by_user(
            user_id=user.id,
            campaign_id=campaign_id,
            status=normalized_status,
            channel=normalized_channel,
        )
        return PostListResponse(posts=[self._to_response(post) for post in posts])

    async def get_post(self, user: User, post_id: UUID) -> PostResponse:
        post = await self.repository.get_post_by_id_for_user(post_id, user.id)
        if post is None:
            raise exceptions.PostNotFound()
        return self._to_response(post)

    async def update_post(
        self,
        user: User,
        post_id: UUID,
        payload: PostUpdateRequest,
    ) -> PostResponse:
        post = await self.repository.get_post_by_id_for_user(post_id, user.id)
        if post is None:
            raise exceptions.PostNotFound()

        campaign = await self.repository.get_campaign_by_id_for_user(post.campaign_id, user.id)
        if campaign is None:
            raise exceptions.PostCampaignNotFound()

        update_fields = payload.model_fields_set
        update_body = "body" in update_fields
        update_scheduled_for = "scheduled_for" in update_fields
        update_status = "status" in update_fields
        replace_remote_image_urls = "image_urls" in update_fields

        if update_scheduled_for:
            self._ensure_schedule_is_editable(post)
        normalized_scheduled_for = (
            self._normalize_datetime(payload.scheduled_for, require_timezone=payload.scheduled_for is not None)
            if update_scheduled_for
            else None
        )
        normalized_status = None
        if update_status:
            normalized_status = self._normalize_status(payload.status, editable_only=True)
            if post.status not in EDITABLE_POST_STATUSES:
                raise exceptions.PostScheduleStatusInvalid(post.status)

        if update_scheduled_for:
            if normalized_scheduled_for is not None:
                self._validate_schedule_for_campaign(campaign, payload.scheduled_for)
                normalized_status = "scheduled"
                update_status = True
            elif not update_status and post.status == "scheduled":
                normalized_status = "draft"
                update_status = True

        if update_status and normalized_status == "scheduled" and normalized_scheduled_for is None:
            if not update_scheduled_for and post.scheduled_for is None:
                raise exceptions.PostScheduledStatusRequiresDatetime()

        if update_status and normalized_status == "draft" and not update_scheduled_for and post.scheduled_for is not None:
            normalized_scheduled_for = None
            update_scheduled_for = True

        updated_post = await self.repository.update_post(
            post,
            body=payload.body.strip() if payload.body else None,
            update_body=update_body,
            scheduled_for=normalized_scheduled_for,
            update_scheduled_for=update_scheduled_for,
            status=normalized_status,
            update_status=update_status,
            remote_image_urls=[str(url) for url in payload.image_urls or []],
            replace_remote_image_urls=replace_remote_image_urls,
        )
        return self._to_response(updated_post)

    async def delete_post(self, user: User, post_id: UUID) -> PostMessageResponse:
        post = await self.repository.get_post_by_id_for_user(post_id, user.id)
        if post is None:
            raise exceptions.PostNotFound()

        await self.repository.soft_delete_post(post)
        return PostMessageResponse(message="Post deleted successfully.")

    async def publish_now(self, user: User, post_id: UUID) -> PostMessageResponse:
        post = await self.repository.get_post_by_id_for_user(post_id, user.id)
        if post is None:
            raise exceptions.PostNotFound()

        self._ensure_publish_dependencies_configured()
        if self.channel_repository is None or self.facebook_provider is None:
            raise RuntimeError("PostService publishing dependencies are not configured.")

        if post.status not in EDITABLE_POST_STATUSES:
            raise exceptions.PostPublishNowStatusInvalid(post.status)

        try:
            external_post_id = await self._publish_post_and_extract_external_id(post)
        except (channel_exceptions.FacebookPublishFailed, channel_exceptions.InstagramPublishFailed) as exc:
            await self.repository.mark_post_publish_failed(
                post,
                error_message=str(exc.message),
            )
            raise exceptions.PostPublishNowFailed() from exc

        await self.repository.mark_post_published_now(
            post,
            external_post_id=external_post_id,
            published_at=datetime.now(timezone.utc),
        )
        return PostMessageResponse(message="Post published successfully.")

    async def schedule_campaign_posts(
        self,
        user: User,
        campaign_id: UUID,
        *,
        time_of_day: str,
        timezone_name: str,
    ) -> list[Post]:
        campaign = await self.repository.get_campaign_by_id_for_user(campaign_id, user.id)
        if campaign is None:
            raise campaign_exceptions.CampaignNotFound()

        timezone_info = self._parse_timezone(timezone_name)
        local_time = self._parse_time_of_day(time_of_day)
        candidates = await self.repository.list_bulk_schedule_candidates(
            user_id=user.id,
            campaign_id=campaign.id,
        )
        occupied_slots = set(await self.repository.list_campaign_occupied_scheduled_datetimes(campaign.id))

        posts_to_schedule: list[tuple[Post, datetime]] = []
        candidate_index = 0
        window_start = campaign.start_date
        while window_start <= campaign.end_date and candidate_index < len(candidates):
            window_end = min(
                campaign.end_date,
                window_start + timedelta(days=campaign.interval_days - 1),
            )
            for local_date in self._build_window_schedule_dates(
                start_date=window_start,
                end_date=window_end,
                posts_per_interval=campaign.posts_per_interval,
            ):
                if candidate_index >= len(candidates):
                    break
                scheduled_for = self._reserve_campaign_slot(
                    local_date=local_date,
                    time_of_day=local_time,
                    timezone_info=timezone_info,
                    occupied_slots=occupied_slots,
                )
                posts_to_schedule.append((candidates[candidate_index], scheduled_for))
                candidate_index += 1

            window_start = window_start + timedelta(days=campaign.interval_days)

        scheduled_posts = await self.repository.bulk_schedule_posts(posts_to_schedule)
        return scheduled_posts

    async def publish_due_scheduled_posts(self, *, limit: int = 25) -> ScheduledPostsPublishResult:
        self._ensure_publish_dependencies_configured()
        claimed_posts = await self.repository.claim_due_scheduled_posts(
            now=datetime.now(timezone.utc),
            limit=limit,
        )

        published_count = 0
        failed_count = 0
        for post in claimed_posts:
            try:
                external_post_id = await self._publish_post_and_extract_external_id(post)
            except Exception as exc:  # pragma: no cover - defensive background path
                failed_count += 1
                await self.repository.mark_post_publish_failed(
                    post,
                    error_message=self._get_publish_error_message(exc),
                )
                continue

            await self.repository.mark_post_published_now(
                post,
                external_post_id=external_post_id,
                published_at=datetime.now(timezone.utc),
            )
            published_count += 1

        return ScheduledPostsPublishResult(
            claimed=len(claimed_posts),
            published=published_count,
            failed=failed_count,
        )

    async def _publish_post_and_extract_external_id(self, post: Post) -> str:
        selected_page = await self._get_selected_page_for_user(post.user_id)
        provider_response = await self._publish_post(post, selected_page)
        external_post_id = str(provider_response.get("id", "")).strip()
        if external_post_id:
            return external_post_id
        if post.channel == INSTAGRAM_PROVIDER:
            raise channel_exceptions.InstagramPublishFailed()
        raise channel_exceptions.FacebookPublishFailed()

    async def _get_selected_page_for_user(self, user_id: UUID):
        if self.channel_repository is None:
            raise RuntimeError("PostService publishing dependencies are not configured.")
        connection = await self.channel_repository.get_connection_by_user_and_provider(
            user_id=user_id,
            provider=FACEBOOK_PROVIDER,
        )
        if connection is None:
            raise channel_exceptions.ChannelConnectionNotFound(FACEBOOK_PROVIDER)
        selected_page = connection.selected_facebook_page
        if selected_page is None:
            raise channel_exceptions.FacebookSelectedPageNotFound(FACEBOOK_PROVIDER)
        return selected_page

    async def _publish_post(self, post: Post, selected_page) -> dict:
        publisher = self.publishers.get(post.channel)
        if publisher is None:
            raise exceptions.PostPublishNowChannelUnsupported(post.channel)
        return await publisher.publish(post, selected_page)

    def _ensure_publish_dependencies_configured(self) -> None:
        if self.channel_repository is None or self.facebook_provider is None:
            raise RuntimeError("PostService publishing dependencies are not configured.")

    def _ensure_schedule_is_editable(self, post: Post) -> None:
        if post.status not in EDITABLE_POST_STATUSES:
            raise exceptions.PostScheduleStatusInvalid(post.status)

    async def upload_images(
        self,
        user: User,
        post_id: UUID,
        files: list[UploadFile],
    ) -> PostResponse:
        post = await self.repository.get_post_by_id_for_user(post_id, user.id)
        if post is None:
            raise exceptions.PostNotFound()

        upload_root = self._get_upload_root()
        post_dir = upload_root / str(user.id) / str(post.id)
        post_dir.mkdir(parents=True, exist_ok=True)

        image_payloads: list[dict[str, str | None]] = []
        written_files: list[Path] = []
        try:
            for file in files:
                extension = Path(file.filename or "").suffix
                generated_name = f"{uuid4().hex}{extension}"
                destination = post_dir / generated_name
                file_bytes = await file.read()
                destination.write_bytes(file_bytes)
                written_files.append(destination)

                relative_path = destination.relative_to(upload_root).as_posix()
                image_payloads.append(
                    {
                        "storage_type": UPLOADED_FILE_STORAGE_TYPE,
                        "file_url": self._build_public_url(relative_path),
                        "file_path": relative_path,
                        "original_filename": file.filename,
                        "mime_type": file.content_type,
                    }
                )
        except Exception:
            for written_file in written_files:
                written_file.unlink(missing_ok=True)
            raise
        finally:
            for file in files:
                await file.close()

        updated_post = await self.repository.append_post_images(post, image_payloads)
        return self._to_response(updated_post)

    async def attach_image_urls(
        self,
        user: User,
        post_id: UUID,
        payload: AttachImageUrlsRequest,
    ) -> PostResponse:
        post = await self.repository.get_post_by_id_for_user(post_id, user.id)
        if post is None:
            raise exceptions.PostNotFound()

        image_payloads = [
            {
                "storage_type": REMOTE_URL_STORAGE_TYPE,
                "file_url": str(image_url),
                "file_path": None,
                "original_filename": None,
                "mime_type": None,
            }
            for image_url in payload.image_urls
        ]
        updated_post = await self.repository.append_post_images(post, image_payloads)
        return self._to_response(updated_post)

    async def delete_image(self, user: User, post_id: UUID, image_id: UUID) -> PostResponse:
        post = await self.repository.get_post_by_id_for_user(post_id, user.id)
        if post is None:
            raise exceptions.PostNotFound()

        image = await self.repository.get_post_image_for_post(post.id, image_id)
        if image is None:
            raise exceptions.PostImageNotFound()

        if image.storage_type == UPLOADED_FILE_STORAGE_TYPE and image.file_path:
            file_path = self._get_upload_root() / image.file_path
            file_path.unlink(missing_ok=True)

        await self.repository.delete_post_image(image)
        refreshed_post = await self.repository.get_post_by_id_for_user(post.id, user.id)
        return self._to_response(refreshed_post)

    def _normalize_channel(self, channel: str) -> str:
        normalized = channel.strip().lower()
        if normalized not in ALLOWED_POST_CHANNELS:
            raise exceptions.PostChannelInvalid(normalized)
        return normalized

    def _ensure_channel_is_targeted(self, channel: str, campaign) -> None:
        targeted_channels = {campaign_channel.channel for campaign_channel in campaign.channels}
        if channel not in targeted_channels:
            raise exceptions.PostChannelNotAllowedForCampaign(channel)

    def _normalize_status(self, status: str | None, *, editable_only: bool = False) -> str:
        normalized = (status or "").strip().lower()
        if normalized not in ALLOWED_POST_STATUSES:
            raise exceptions.PostStatusInvalid(normalized)
        if editable_only and normalized not in EDITABLE_POST_STATUSES:
            raise exceptions.PostStatusNotEditable(normalized)
        return normalized

    def _normalize_datetime(
        self,
        value: datetime | None,
        *,
        require_timezone: bool = False,
    ) -> datetime | None:
        if value is None:
            return None
        if require_timezone and (value.tzinfo is None or value.utcoffset() is None):
            raise exceptions.PostScheduleTimezoneRequired()
        if value.tzinfo is None or value.utcoffset() is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def _validate_schedule_for_campaign(self, campaign, scheduled_for: datetime | None) -> None:
        if scheduled_for is None:
            return
        scheduled_date = scheduled_for.date()
        if scheduled_date < campaign.start_date or scheduled_date > campaign.end_date:
            raise exceptions.PostScheduleOutsideCampaignRange(
                scheduled_date=scheduled_date.isoformat(),
                start_date=campaign.start_date.isoformat(),
                end_date=campaign.end_date.isoformat(),
            )

    def _parse_timezone(self, value: str) -> ZoneInfo:
        try:
            return ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise campaign_exceptions.CampaignScheduleTimezoneInvalid(value) from exc

    def _parse_time_of_day(self, value: str) -> time:
        try:
            parsed = time.fromisoformat(value)
        except ValueError as exc:
            raise campaign_exceptions.CampaignScheduleTimeInvalid(value) from exc
        return parsed.replace(tzinfo=None)

    def _build_window_schedule_dates(
        self,
        *,
        start_date: date,
        end_date: date,
        posts_per_interval: int,
    ) -> list[date]:
        window_days = max((end_date - start_date).days + 1, 1)
        if posts_per_interval == 1:
            return [start_date]

        max_offset = max(window_days - 1, 0)
        schedule_dates: list[date] = []
        for index in range(posts_per_interval):
            if max_offset == 0:
                day_offset = 0
            else:
                day_offset = round(index * max_offset / (posts_per_interval - 1))
            schedule_dates.append(start_date + timedelta(days=day_offset))
        return schedule_dates

    def _reserve_campaign_slot(
        self,
        *,
        local_date: date,
        time_of_day: time,
        timezone_info: ZoneInfo,
        occupied_slots: set[datetime],
    ) -> datetime:
        local_datetime = datetime.combine(local_date, time_of_day, tzinfo=timezone_info)
        candidate = local_datetime.astimezone(timezone.utc)
        while candidate in occupied_slots:
            local_datetime = local_datetime + timedelta(minutes=5)
            candidate = local_datetime.astimezone(timezone.utc)
        occupied_slots.add(candidate)
        return candidate

    def _get_publish_error_message(self, exc: Exception) -> str:
        if isinstance(exc, AppException):
            return exc.message
        return "Publishing the scheduled post failed."

    def _get_upload_root(self) -> Path:
        configured_path = Path(settings.post_upload_dir)
        if configured_path.is_absolute():
            return configured_path
        return BASE_DIR / configured_path

    def _build_public_url(self, relative_path: str) -> str:
        return f"{settings.post_media_url_prefix}/{relative_path.replace('\\', '/')}"

    def to_response(self, post: Post) -> PostResponse:
        return self._to_response(post)

    def _to_response(self, post: Post) -> PostResponse:
        images = sorted(post.images, key=lambda image: (image.sort_order, image.created_at))
        return PostResponse(
            id=post.id,
            user_id=post.user_id,
            campaign_id=post.campaign_id,
            content_plan_item_id=post.content_plan_item_id,
            channel=post.channel,
            body=post.body,
            image_prompt=post.image_prompt,
            status=post.status,
            scheduled_for=post.scheduled_for,
            published_at=post.published_at,
            external_post_id=post.external_post_id,
            error_message=post.error_message,
            images=[self._to_image_response(image) for image in images],
            created_at=post.created_at,
            updated_at=post.updated_at,
            deleted_at=post.deleted_at,
        )

    def _to_image_response(self, image: PostImage) -> PostImageResponse:
        return PostImageResponse(
            id=image.id,
            storage_type=image.storage_type,
            url=image.file_url,
            original_filename=image.original_filename,
            mime_type=image.mime_type,
            sort_order=image.sort_order,
        )
