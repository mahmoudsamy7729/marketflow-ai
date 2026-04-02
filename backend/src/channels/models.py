from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class ChannelConnection(Base):
    __tablename__ = "channel_connections"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="connected")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    facebook_details: Mapped["FacebookConnectionDetails | None"] = relationship(
        back_populates="connection",
        uselist=False,
        cascade="all, delete-orphan",
    )
    selected_facebook_page: Mapped["FacebookSelectedPage | None"] = relationship(
        back_populates="connection",
        uselist=False,
        cascade="all, delete-orphan",
    )
class FacebookConnectionDetails(Base):
    __tablename__ = "facebook_connection_details"

    connection_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("channel_connections.id", ondelete="CASCADE"),
        primary_key=True,
    )
    facebook_user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    token_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    granted_scopes: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    connection: Mapped[ChannelConnection] = relationship(back_populates="facebook_details")


class FacebookSelectedPage(Base):
    __tablename__ = "facebook_selected_pages"

    connection_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("channel_connections.id", ondelete="CASCADE"),
        primary_key=True,
    )
    facebook_page_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    page_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    page_access_token: Mapped[str] = mapped_column(Text, nullable=False)
    tasks: Mapped[str | None] = mapped_column(Text, nullable=True)
    instagram_account_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    instagram_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    instagram_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    instagram_profile_picture_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    connection: Mapped[ChannelConnection] = relationship(back_populates="selected_facebook_page")


class OAuthState(Base):
    __tablename__ = "oauth_states"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
