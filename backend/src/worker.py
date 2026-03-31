import os

from celery import Celery


broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
result_backend = os.getenv("CELERY_RESULT_BACKEND", broker_url)

celery_app = Celery("postiz", broker=broker_url, backend=result_backend)
celery_app.conf.update(
    accept_content=["json"],
    enable_utc=True,
    result_serializer="json",
    task_serializer="json",
    timezone=os.getenv("TZ", "UTC"),
)


@celery_app.task(name="postiz.healthcheck")
def healthcheck() -> str:
    return "ok"
