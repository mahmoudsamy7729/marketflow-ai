from __future__ import annotations

from fastapi.concurrency import run_in_threadpool
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


async def hash_password(password: str) -> str:
    return await run_in_threadpool(pwd_context.hash, password)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return await run_in_threadpool(
        pwd_context.verify,
        plain_password,
        hashed_password,
    )
