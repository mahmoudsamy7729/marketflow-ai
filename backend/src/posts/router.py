from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, Query, UploadFile, status

from src.dependencies import current_user_dependency
from src.posts.dependencies import post_service_dependency
from src.posts.schemas import (
    AttachImageUrlsRequest,
    PostCreateRequest,
    PostListResponse,
    PostMessageResponse,
    PostResponse,
    PostUpdateRequest,
)


router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    payload: PostCreateRequest,
    current_user: current_user_dependency,
    service: post_service_dependency,
) -> PostResponse:
    return await service.create_post(current_user, payload)


@router.get("", response_model=PostListResponse)
async def list_posts(
    current_user: current_user_dependency,
    service: post_service_dependency,
    campaign_id: UUID | None = Query(default=None),
    status: str | None = Query(default=None),
    channel: str | None = Query(default=None),
) -> PostListResponse:
    return await service.list_posts(
        current_user,
        campaign_id=campaign_id,
        status=status,
        channel=channel,
    )


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: UUID,
    current_user: current_user_dependency,
    service: post_service_dependency,
) -> PostResponse:
    return await service.get_post(current_user, post_id)


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: UUID,
    payload: PostUpdateRequest,
    current_user: current_user_dependency,
    service: post_service_dependency,
) -> PostResponse:
    return await service.update_post(current_user, post_id, payload)


@router.delete("/{post_id}", response_model=PostMessageResponse)
async def delete_post(
    post_id: UUID,
    current_user: current_user_dependency,
    service: post_service_dependency,
) -> PostMessageResponse:
    return await service.delete_post(current_user, post_id)


@router.post("/{post_id}/publish-now", response_model=PostMessageResponse)
async def publish_post_now(
    post_id: UUID,
    current_user: current_user_dependency,
    service: post_service_dependency,
) -> PostMessageResponse:
    return await service.publish_now(current_user, post_id)


@router.post("/{post_id}/images/upload", response_model=PostResponse)
async def upload_post_images(
    post_id: UUID,
    current_user: current_user_dependency,
    service: post_service_dependency,
    files: Annotated[list[UploadFile], File(...)],
) -> PostResponse:
    return await service.upload_images(current_user, post_id, files)


@router.post("/{post_id}/images/attach-urls", response_model=PostResponse)
async def attach_post_image_urls(
    post_id: UUID,
    payload: AttachImageUrlsRequest,
    current_user: current_user_dependency,
    service: post_service_dependency,
) -> PostResponse:
    return await service.attach_image_urls(current_user, post_id, payload)


@router.delete("/{post_id}/images/{image_id}", response_model=PostResponse)
async def delete_post_image(
    post_id: UUID,
    image_id: UUID,
    current_user: current_user_dependency,
    service: post_service_dependency,
) -> PostResponse:
    return await service.delete_image(current_user, post_id, image_id)
