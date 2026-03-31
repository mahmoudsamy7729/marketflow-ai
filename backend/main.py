from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from src.auth.router import router as auth_router
from src.campaigns.router import router as campaigns_router
from src.channels.router import router as channels_router
from src.common.exceptions import AppException
from src.config import BASE_DIR, settings
from src.posts.router import router as posts_router


app = FastAPI(title=settings.app_name, debug=settings.app_debug)

post_upload_root = Path(settings.post_upload_dir)
if not post_upload_root.is_absolute():
    post_upload_root = BASE_DIR / post_upload_root
post_upload_root.mkdir(parents=True, exist_ok=True)
app.mount(
    settings.post_media_url_prefix,
    StaticFiles(directory=post_upload_root),
    name="post-media",
)


@app.exception_handler(AppException)
async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "extra": exc.extra or {},
            }
        },
    )


app.include_router(auth_router)
app.include_router(campaigns_router)
app.include_router(channels_router)
app.include_router(posts_router)
