"""
Pydantic schemas for User / Auth endpoints.

Separates request bodies (Create) from response bodies (Response)
to avoid leaking sensitive fields like password_hash.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ── Registration / Login ──────────────────────────────────────────────────

class UserRegister(BaseModel):
    name: str = Field(..., min_length=1, max_length=120, examples=["Tejas Prasad"])
    email: EmailStr = Field(..., examples=["tejas@example.com"])
    phone: str | None = Field(None, max_length=20, examples=["+919876543210"])
    password: str = Field(..., min_length=8, examples=["Str0ngP@ss!"])


class UserLogin(BaseModel):
    email: EmailStr = Field(..., examples=["tejas@example.com"])
    password: str = Field(..., examples=["Str0ngP@ss!"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── User Response ─────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    phone: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Store ─────────────────────────────────────────────────────────────────

class StoreCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, examples=["Downtown Bistro"])
    location: str | None = Field(None, examples=["123 MG Road, Bangalore"])


class StoreResponse(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    location: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── POS Terminal ──────────────────────────────────────────────────────────

class POSTerminalCreate(BaseModel):
    store_id: UUID
    device_name: str = Field(..., max_length=120, examples=["Counter-1 iPad"])
    device_identifier: str = Field(..., max_length=255, examples=["IPAD-A1B2C3"])


class POSTerminalResponse(BaseModel):
    id: UUID
    store_id: UUID
    device_name: str
    device_identifier: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Employee ──────────────────────────────────────────────────────────────

class EmployeeCreate(BaseModel):
    store_id: UUID
    name: str = Field(..., max_length=120, examples=["Ravi Kumar"])
    employee_code: str = Field(..., max_length=20, examples=["EMP001"])
    pin: str = Field(..., max_length=10, examples=["1234"])
    role: str = Field("cashier", max_length=50, examples=["cashier"])


class EmployeeResponse(BaseModel):
    id: UUID
    store_id: UUID
    name: str
    employee_code: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Dine-In Table ────────────────────────────────────────────────────────

class DineInTableCreate(BaseModel):
    store_id: UUID
    table_number: int = Field(..., ge=1, examples=[1])
    capacity: int = Field(4, ge=1, examples=[4])
    status: str = Field("available", examples=["available"])


class DineInTableResponse(BaseModel):
    id: UUID
    store_id: UUID
    table_number: int
    capacity: int
    status: str

    model_config = {"from_attributes": True}


# ── Expense ───────────────────────────────────────────────────────────────

class ExpenseCreate(BaseModel):
    store_id: UUID
    title: str = Field(..., max_length=200, examples=["Vegetable purchase"])
    amount: float = Field(..., gt=0, examples=[1500.00])
    category: str | None = Field(None, max_length=100, examples=["ingredients"])


class ExpenseResponse(BaseModel):
    id: UUID
    store_id: UUID
    title: str
    amount: float
    category: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
