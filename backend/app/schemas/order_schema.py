"""
Pydantic schemas for Order, OrderItem, Payment, Sync, and Analytics endpoints.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ── Order Item ────────────────────────────────────────────────────────────

class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(1, ge=1)
    price: float = Field(..., ge=0, examples=[299.00])


class OrderItemResponse(BaseModel):
    id: UUID
    order_id: UUID
    product_id: UUID | None
    quantity: int
    price: float
    total: float

    model_config = {"from_attributes": True}


# ── Order ─────────────────────────────────────────────────────────────────

class OrderCreate(BaseModel):
    store_id: UUID
    employee_id: UUID | None = None
    terminal_id: UUID | None = None
    table_id: UUID | None = None
    order_type: str = Field("dine_in", examples=["dine_in", "takeaway", "delivery"])
    discount_amount: float = Field(0.0, ge=0)
    items: list[OrderItemCreate] = Field(..., min_length=1)


class OrderResponse(BaseModel):
    id: UUID
    store_id: UUID
    employee_id: UUID | None
    terminal_id: UUID | None
    table_id: UUID | None
    order_type: str
    gross_amount: float
    tax_amount: float
    discount_amount: float
    net_amount: float
    payment_status: str
    device_id: str | None
    sync_status: str | None
    created_at: datetime
    items: list[OrderItemResponse] = []

    model_config = {"from_attributes": True}


class OrderComplete(BaseModel):
    """Mark an order as completed."""
    payment_status: str = Field("completed", examples=["completed"])


# ── Payment ───────────────────────────────────────────────────────────────

class PaymentCreate(BaseModel):
    order_id: UUID
    payment_method: str = Field(..., examples=["cash", "card", "upi"])
    amount: float = Field(..., gt=0, examples=[500.00])


class PaymentResponse(BaseModel):
    id: UUID
    order_id: UUID
    payment_method: str
    amount: float
    paid_at: datetime
    device_id: str | None
    sync_status: str | None

    model_config = {"from_attributes": True}


# ── Sync (offline POS → server) ──────────────────────────────────────────

class SyncOrderItem(BaseModel):
    product_id: UUID
    quantity: int = Field(1, ge=1)
    price: float = Field(..., ge=0)


class SyncOrder(BaseModel):
    """An order originating from an offline POS device."""
    device_id: str = Field(..., max_length=255)
    store_id: UUID
    employee_id: UUID | None = None
    terminal_id: UUID | None = None
    table_id: UUID | None = None
    order_type: str = "dine_in"
    discount_amount: float = 0.0
    items: list[SyncOrderItem] = Field(..., min_length=1)
    created_at: datetime  # original creation time on device


class SyncOrdersRequest(BaseModel):
    orders: list[SyncOrder] = Field(..., min_length=1)


class SyncPayment(BaseModel):
    """A payment recorded offline on a POS device."""
    device_id: str = Field(..., max_length=255)
    order_id: UUID
    payment_method: str
    amount: float = Field(..., gt=0)
    paid_at: datetime


class SyncPaymentsRequest(BaseModel):
    payments: list[SyncPayment] = Field(..., min_length=1)


class SyncResponse(BaseModel):
    synced: int
    failed: int
    errors: list[str] = []


# ── Analytics ─────────────────────────────────────────────────────────────

class AnalyticsSummary(BaseModel):
    total_revenue: float
    total_orders: int
    tax_collected: float
    gross_sales: float
    net_sales: float
    total_discounts: float
    payment_breakdown: dict[str, float]  # {"cash": ..., "card": ..., "upi": ...}
