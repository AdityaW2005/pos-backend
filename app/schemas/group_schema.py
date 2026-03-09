"""Pydantic schemas for Permission Groups (admin & biller groups)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PermissionGroupCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, examples=["Floor Managers"])
    group_type: str = Field("admin", examples=["admin", "biller"])
    permissions: list[str] = Field(default_factory=list, examples=[["orders.view", "orders.cancel"]])
    store_ids: list[UUID] = Field(default_factory=list)
    member_user_ids: list[UUID] = Field(default_factory=list)


class PermissionGroupUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    permissions: list[str] | None = None
    is_active: bool | None = None
    store_ids: list[UUID] | None = None
    member_user_ids: list[UUID] | None = None


class PermissionGroupResponse(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    group_type: str
    permissions: list | None
    is_active: bool
    store_ids: list[UUID] = []
    member_user_ids: list[UUID] = []
    created_at: datetime

    model_config = {"from_attributes": True}
