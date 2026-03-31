from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    access_token_secret_key: str = Field(
        validation_alias=AliasChoices(
            "ACCESS_TOKEN_SECRET_KEY",
            "access_token_secret_key",
        ),
    )
    refresh_token_secret_key: str = Field(
        validation_alias=AliasChoices(
            "REFRESH_TOKEN_SECRET_KEY",
            "refresh_token_secret_key",
        ),
    )
    algorithm: str = Field(
        default="HS256",
        validation_alias=AliasChoices("ALGORITHM", "algorithm"),
    )
    access_token_expire_minutes: int = Field(
        default=15,
        validation_alias=AliasChoices(
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            "access_token_expire_minutes",
        ),
    )
    refresh_token_expire_minutes: int = Field(
        default=10080,
        validation_alias=AliasChoices(
            "REFRESH_TOKEN_EXPIRE_MINUTES",
            "refresh_token_expire_minutes",
        ),
    )
    access_token_cookie_name: str = Field(
        default="access_token",
        validation_alias=AliasChoices(
            "ACCESS_TOKEN_COOKIE_NAME",
            "access_token_cookie_name",
        ),
    )
    refresh_token_cookie_name: str = Field(
        default="refresh_token",
        validation_alias=AliasChoices(
            "REFRESH_TOKEN_COOKIE_NAME",
            "refresh_token_cookie_name",
        ),
    )
    cookie_secure: bool = Field(
        default=False,
        validation_alias=AliasChoices("COOKIE_SECURE", "cookie_secure"),
    )
    cookie_samesite: str = Field(
        default="lax",
        validation_alias=AliasChoices("COOKIE_SAMESITE", "cookie_samesite"),
    )
    cookie_domain: str | None = Field(
        default=None,
        validation_alias=AliasChoices("COOKIE_DOMAIN", "cookie_domain"),
    )

    @field_validator("cookie_samesite")
    @classmethod
    def normalize_samesite(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"lax", "strict", "none"}:
            raise ValueError("COOKIE_SAMESITE must be one of lax, strict, or none.")
        return normalized

    @field_validator("cookie_domain")
    @classmethod
    def normalize_cookie_domain(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None
