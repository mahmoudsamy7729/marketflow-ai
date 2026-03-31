from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from jose import JWTError, ExpiredSignatureError, jwt

from src.auth import exceptions
from src.config import settings


ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def _generate_token(
    subject: UUID,
    expires_in_minutes: int,
    secret_key: str,
    token_type: str,
) -> tuple[str, datetime]:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expires_in_minutes)
    payload = {
        "sub": str(subject),
        "type": token_type,
        "iat": now,
        "exp": expire,
        "jti": str(uuid4()),
    }
    token = jwt.encode(payload, secret_key, algorithm=settings.algorithm)
    return token, expire


def generate_access_token(subject: UUID) -> tuple[str, datetime]:
    return _generate_token(
        subject=subject,
        expires_in_minutes=settings.access_token_expire_minutes,
        secret_key=settings.access_token_secret_key,
        token_type=ACCESS_TOKEN_TYPE,
    )


def generate_refresh_token(subject: UUID) -> tuple[str, datetime]:
    return _generate_token(
        subject=subject,
        expires_in_minutes=settings.refresh_token_expire_minutes,
        secret_key=settings.refresh_token_secret_key,
        token_type=REFRESH_TOKEN_TYPE,
    )


def _verify_token(token: str, secret_key: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[settings.algorithm])
    except ExpiredSignatureError as exc:
        raise exceptions.TokenExpired() from exc
    except JWTError as exc:
        raise exceptions.InvalidToken() from exc

    subject = payload.get("sub")
    token_type = payload.get("type")
    if not subject or token_type != expected_type:
        raise exceptions.InvalidTokenPayload()

    return payload


def verify_access_token(token: str) -> dict:
    return _verify_token(
        token=token,
        secret_key=settings.access_token_secret_key,
        expected_type=ACCESS_TOKEN_TYPE,
    )


def verify_refresh_token(token: str) -> dict:
    return _verify_token(
        token=token,
        secret_key=settings.refresh_token_secret_key,
        expected_type=REFRESH_TOKEN_TYPE,
    )
