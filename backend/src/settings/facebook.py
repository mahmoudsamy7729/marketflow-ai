from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings


class FacebookSettings(BaseSettings):
    facebook_app_id: str = Field(
        default="",
        validation_alias=AliasChoices("FACEBOOK_APP_ID", "facebook_app_id"),
    )
    facebook_app_secret: str = Field(
        default="",
        validation_alias=AliasChoices("FACEBOOK_APP_SECRET", "facebook_app_secret"),
    )
    facebook_redirect_uri: str = Field(
        default="",
        validation_alias=AliasChoices(
            "FACEBOOK_REDIRECT_URI",
            "facebook_redirect_uri",
        ),
    )
    facebook_config_id: str = Field(
        default="",
        validation_alias=AliasChoices(
            "FACEBOOK_CONFIG_ID",
            "facebook_config_id",
        ),
    )
    facebook_oauth_scopes: str = Field(
        default="public_profile",
        validation_alias=AliasChoices(
            "FACEBOOK_OAUTH_SCOPES",
            "facebook_oauth_scopes",
        ),
    )
    facebook_api_version: str = Field(
        default="v22.0",
        validation_alias=AliasChoices(
            "FACEBOOK_API_VERSION",
            "facebook_api_version",
        ),
    )
    facebook_state_expire_minutes: int = Field(
        default=10,
        validation_alias=AliasChoices(
            "FACEBOOK_STATE_EXPIRE_MINUTES",
            "facebook_state_expire_minutes",
        ),
    )

    @field_validator("facebook_oauth_scopes")
    @classmethod
    def normalize_facebook_scopes(cls, value: str) -> str:
        scopes = [scope.strip() for scope in value.split(",") if scope.strip()]
        return ",".join(scopes) if scopes else "public_profile"
