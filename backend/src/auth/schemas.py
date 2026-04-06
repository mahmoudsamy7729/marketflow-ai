from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RegisterRequest(BaseModel):
    email: str
    company_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("Email is required.")
        return normalized

    @field_validator("company_name")
    @classmethod
    def normalize_company_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Company name is required.")
        return normalized


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("Email is required.")
        return normalized


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    company_name: str
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class AuthSessionResponse(BaseModel):
    access_token: str
    user: UserResponse


class MessageResponse(BaseModel):
    message: str
