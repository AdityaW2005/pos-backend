"""Pydantic schemas for Notification and DeviceToken endpoints."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ── Notification ──────────────────────────────────────────────────────────

class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    store_id: UUID | None
    title: str
    body: str | None
    category: str
    entity_type: str | None
    entity_id: UUID | None
    is_read: bool
    data: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationMarkRead(BaseModel):
    is_read: bool = True


# ── Device Token ──────────────────────────────────────────────────────────

class DeviceTokenCreate(BaseModel):
    platform: str = Field(..., max_length=20, examples=["fcm", "apns", "web"])
    token: str = Field(..., max_length=500)
    device_name: str | None = Field(None, max_length=120)


class DeviceTokenResponse(BaseModel):
    id: UUID
    user_id: UUID
    platform: str
    token: str
    device_name: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
