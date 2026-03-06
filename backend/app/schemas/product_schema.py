"""
Pydantic schemas for Category & Product endpoints.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ── Category ──────────────────────────────────────────────────────────────

class CategoryCreate(BaseModel):
    store_id: UUID
    name: str = Field(..., min_length=1, max_length=120, examples=["Beverages"])


class CategoryResponse(BaseModel):
    id: UUID
    store_id: UUID
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Product ───────────────────────────────────────────────────────────────

class ProductCreate(BaseModel):
    store_id: UUID
    category_id: UUID | None = None
    name: str = Field(..., min_length=1, max_length=200, examples=["Paneer Butter Masala"])
    description: str | None = Field(None, examples=["Rich creamy paneer dish"])
    price: float = Field(..., gt=0, examples=[299.00])
    tax_percent: float = Field(0.0, ge=0, le=100, examples=[5.0])
    is_active: bool = True


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(None, gt=0)
    tax_percent: float | None = Field(None, ge=0, le=100)
    is_active: bool | None = None
    category_id: UUID | None = None


class ProductResponse(BaseModel):
    id: UUID
    store_id: UUID
    category_id: UUID | None
    name: str
    description: str | None
    price: float
    tax_percent: float
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
