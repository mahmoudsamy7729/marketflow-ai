from __future__ import annotations

from typing import Protocol

from src.posts.models import Post


class PostPublisher(Protocol):
    async def publish(self, post: Post, selected_page) -> dict: ...
