from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_email(
        self,
        email: str,
        include_deleted: bool = False,
    ) -> User | None:
        statement = select(User).where(User.email == email)
        if not include_deleted:
            statement = statement.where(User.deleted_at.is_(None))

        return await self.session.scalar(statement)

    async def get_by_id(
        self,
        user_id: UUID,
        include_deleted: bool = False,
    ) -> User | None:
        statement = select(User).where(User.id == user_id)
        if not include_deleted:
            statement = statement.where(User.deleted_at.is_(None))

        return await self.session.scalar(statement)

    async def create_user(
        self,
        email: str,
        company_name: str,
        hashed_password: str,
    ) -> User:
        user = User(
            email=email,
            company_name=company_name,
            hashed_password=hashed_password,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def soft_delete(self, user: User) -> User:
        user.deleted_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(user)
        return user
