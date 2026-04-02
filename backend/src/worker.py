import asyncio
import logging
import os
from time import monotonic

from celery import Celery
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.channels.providers import FacebookOAuthProvider
from src.channels.repositories import ChannelRepository
from src.config import settings
from src.posts.repositories import PostRepository
from src.posts.services import PostService


logger = logging.getLogger(__name__)
broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
result_backend = os.getenv("CELERY_RESULT_BACKEND", broker_url)
publish_due_posts_task_name = "postiz.publish_due_posts"
publish_due_posts_schedule_seconds = int(os.getenv("CELERY_PUBLISH_DUE_POSTS_INTERVAL_SECONDS", "15"))
publish_due_posts_batch_size = int(os.getenv("CELERY_PUBLISH_DUE_POSTS_BATCH_SIZE", "50"))
publish_due_posts_max_rounds = int(os.getenv("CELERY_PUBLISH_DUE_POSTS_MAX_ROUNDS", "10"))
publish_due_posts_max_runtime_seconds = int(os.getenv("CELERY_PUBLISH_DUE_POSTS_MAX_RUNTIME_SECONDS", "50"))
worker_prefetch_multiplier = int(os.getenv("CELERY_WORKER_PREFETCH_MULTIPLIER", "1"))
task_soft_time_limit_seconds = int(os.getenv("CELERY_TASK_SOFT_TIME_LIMIT_SECONDS", "240"))
task_time_limit_seconds = int(os.getenv("CELERY_TASK_TIME_LIMIT_SECONDS", "300"))

celery_app = Celery("postiz", broker=broker_url, backend=result_backend)
celery_app.conf.update(
    accept_content=["json"],
    beat_schedule={
        "publish-due-posts": {
            "task": publish_due_posts_task_name,
            "schedule": publish_due_posts_schedule_seconds,
        }
    },
    enable_utc=True,
    result_serializer="json",
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_serializer="json",
    task_soft_time_limit=task_soft_time_limit_seconds,
    task_time_limit=task_time_limit_seconds,
    task_track_started=True,
    timezone=os.getenv("TZ", "UTC"),
    worker_prefetch_multiplier=worker_prefetch_multiplier,
)


@celery_app.task(name="postiz.healthcheck")
def healthcheck() -> str:
    return "ok"


@celery_app.task(name=publish_due_posts_task_name)
def publish_due_posts(limit: int | None = None) -> dict[str, int]:
    batch_limit = limit or publish_due_posts_batch_size
    started_at = monotonic()
    rounds = 0
    totals = {
        "claimed": 0,
        "published": 0,
        "failed": 0,
        "rounds": 0,
    }

    while rounds < publish_due_posts_max_rounds:
        elapsed = monotonic() - started_at
        if elapsed >= publish_due_posts_max_runtime_seconds:
            logger.info(
                "Stopping scheduled publish drain because the runtime budget was reached.",
                extra={
                    "elapsed_seconds": round(elapsed, 2),
                    "rounds_completed": rounds,
                    "batch_limit": batch_limit,
                },
            )
            break

        result = asyncio.run(_publish_due_posts_async(batch_limit))
        rounds += 1
        totals["claimed"] += int(result["claimed"])
        totals["published"] += int(result["published"])
        totals["failed"] += int(result["failed"])
        totals["rounds"] = rounds

        logger.info(
            "Scheduled publish batch completed.",
            extra={
                "round": rounds,
                "batch_limit": batch_limit,
                "claimed": result["claimed"],
                "published": result["published"],
                "failed": result["failed"],
            },
        )

        if int(result["claimed"]) < batch_limit:
            break

    logger.info(
        "Scheduled publish drain completed.",
        extra={
            "rounds": totals["rounds"],
            "claimed": totals["claimed"],
            "published": totals["published"],
            "failed": totals["failed"],
            "batch_limit": batch_limit,
        },
    )
    return totals


async def _publish_due_posts_async(limit: int) -> dict[str, int]:
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        poolclass=NullPool,
    )
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    try:
        async with session_factory() as session:
            service = PostService(
                repository=PostRepository(session),
                channel_repository=ChannelRepository(session),
                facebook_provider=FacebookOAuthProvider(),
            )
            result = await service.publish_due_scheduled_posts(limit=limit)
            return result.model_dump()
    finally:
        await engine.dispose()
