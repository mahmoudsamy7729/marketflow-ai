from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings


class N8NSettings(BaseSettings):
    n8n_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("N8N_API_KEY", "n8n_api_key"),
    )
