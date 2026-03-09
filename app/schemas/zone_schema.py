"""Pydantic schemas for Zone management."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ZoneCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, examples=["North Bangalore"])
    state: str | None = Field(None, max_length=100, examples=["Karnataka"])
    city: str | None = Field(None, max_length=100, examples=["Bangalore"])
    sub_order_type: str = Field("delivery", examples=["delivery", "dine_in", "takeaway"])
    delivery_fee: float = Field(0, ge=0)
    min_order_amount: float = Field(0, ge=0)
    boundary: dict | None = None
    store_ids: list[UUID] = Field(default_factory=list)


class ZoneUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    state: str | None = None
    city: str | None = None
    sub_order_type: str | None = None
    delivery_fee: float | None = Field(None, ge=0)
    min_order_amount: float | None = Field(None, ge=0)
    boundary: dict | None = None
    is_active: bool | None = None
    store_ids: list[UUID] | None = None


class ZoneResponse(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    state: str | None
    city: str | None
    sub_order_type: str
    delivery_fee: float
    min_order_amount: float
    boundary: dict | None
    is_active: bool
    store_ids: list[UUID] = []
    created_at: datetime

    model_config = {"from_attributes": True}
