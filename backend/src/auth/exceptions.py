from __future__ import annotations

from src.common.exceptions import AppException


class UserAlreadyExists(AppException):
    def __init__(self, email: str) -> None:
        super().__init__(
            code="user_already_exists",
            message="A user with this email already exists.",
            status_code=409,
            extra={"email": email},
        )


class InvalidCredentials(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="invalid_credentials",
            message="Invalid email or password.",
            status_code=401,
        )


class AuthenticationRequired(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="authentication_required",
            message="Authentication is required.",
            status_code=401,
        )


class InvalidToken(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="invalid_token",
            message="The provided token is invalid.",
            status_code=401,
        )


class InvalidTokenPayload(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="invalid_token_payload",
            message="The token payload is invalid.",
            status_code=401,
        )


class TokenExpired(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="token_expired",
            message="The provided token has expired.",
            status_code=401,
        )


class UserNotFound(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="user_not_found",
            message="User was not found.",
            status_code=404,
        )


class UserDeleted(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="user_deleted",
            message="User is deleted.",
            status_code=410,
        )


class AdminPrivilegesRequired(AppException):
    def __init__(self) -> None:
        super().__init__(
            code="admin_privileges_required",
            message="Admin privileges are required.",
            status_code=403,
        )
