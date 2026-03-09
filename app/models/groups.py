"""
Permission group models – admin groups and biller groups.

- PermissionGroup: a named group of permissions assignable to stores.
- PermissionGroupMember: links users to groups.
- PermissionGroupStore: links groups to stores.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PermissionGroup(Base):
    __tablename__ = "permission_groups"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    # admin | biller
    group_type: Mapped[str] = mapped_column(String(50), nullable=False, default="admin")
    # List of permission strings
    permissions: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    members = relationship("PermissionGroupMember", back_populates="group", cascade="all, delete-orphan")
    stores = relationship("PermissionGroupStore", back_populates="group", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_permission_groups_owner_id", "owner_id"),
        Index("ix_permission_groups_type", "group_type"),
    )


class PermissionGroupMember(Base):
    __tablename__ = "permission_group_members"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("permission_groups.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    group = relationship("PermissionGroup", back_populates="members")

    __table_args__ = (
        Index("ix_pgm_group_id", "group_id"),
        Index("ix_pgm_user_id", "user_id"),
        Index("ix_pgm_unique", "group_id", "user_id", unique=True),
    )


class PermissionGroupStore(Base):
    __tablename__ = "permission_group_stores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("permission_groups.id", ondelete="CASCADE"), nullable=False
    )
    store_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False
    )

    group = relationship("PermissionGroup", back_populates="stores")

    __table_args__ = (
        Index("ix_pgs_group_id", "group_id"),
        Index("ix_pgs_store_id", "store_id"),
        Index("ix_pgs_unique", "group_id", "store_id", unique=True),
    )
