from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select

from src.auth.exceptions import (
    AuthenticationRequired,
    InvalidTokenPayload,
    UserDeleted,
    UserNotFound,
)
from src.auth.jwt import verify_access_token
from src.auth.models import User
from src.database import db_dependency


oauth2_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    db: db_dependency,
    credentials: HTTPAuthorizationCredentials | None = Depends(oauth2_scheme),
) -> User:
    if credentials is None or not credentials.credentials:
        raise AuthenticationRequired()

    payload = verify_access_token(credentials.credentials)
    subject = payload.get("sub")

    try:
        user_id = UUID(str(subject))
    except (TypeError, ValueError) as exc:
        raise InvalidTokenPayload() from exc

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise UserNotFound()
    if user.deleted_at is not None:
        raise UserDeleted()

    return user


current_user_dependency = Annotated[User, Depends(get_current_user)]
user_dependency = current_user_dependency
active_user_dep = current_user_dependency
