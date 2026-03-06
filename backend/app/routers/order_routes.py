"""
Order & Payment routes + Sync endpoints.

POST /orders             → create an order (online POS)
GET  /orders             → list orders for a store
PUT  /orders/{id}/complete → mark order completed
POST /orders/payments    → record a payment
POST /sync/orders        → bulk-sync offline orders
POST /sync/payments      → bulk-sync offline payments
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.orders import Order, Payment
from app.models.users import User
from app.schemas.order_schema import (
    OrderCreate,
    OrderResponse,
    OrderComplete,
    PaymentCreate,
    PaymentResponse,
    SyncOrdersRequest,
    SyncPaymentsRequest,
    SyncResponse,
)
from app.services.order_service import create_order
from app.services.sync_service import sync_orders, sync_payments
from app.utils.auth import get_current_user

router = APIRouter(tags=["Orders"])


# ── Create order ──────────────────────────────────────────────────────────

@router.post(
    "/orders",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order with line items",
)
async def api_create_order(
    payload: OrderCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    order = await create_order(db, payload)
    # Eager-load items for the response
    result = await db.execute(
        select(Order).options(selectinload(Order.items)).where(Order.id == order.id)
    )
    return result.scalar_one()


# ── List orders ───────────────────────────────────────────────────────────

@router.get(
    "/orders",
    response_model=list[OrderResponse],
    summary="List orders for a store",
)
async def list_orders(
    store_id: UUID = Query(...),
    payment_status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = (
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.store_id == store_id)
    )
    if payment_status:
        query = query.where(Order.payment_status == payment_status)
    query = query.order_by(Order.created_at.desc())

    result = await db.execute(query)
    return result.scalars().unique().all()


# ── Complete order ────────────────────────────────────────────────────────

@router.put(
    "/orders/{order_id}/complete",
    response_model=OrderResponse,
    summary="Mark an order as completed",
)
async def complete_order(
    order_id: UUID,
    payload: OrderComplete,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    order.payment_status = payload.payment_status
    await db.flush()
    return order


# ── Payment ───────────────────────────────────────────────────────────────

@router.post(
    "/orders/payments",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a payment for an order",
)
async def create_payment(
    payload: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    # Verify order exists
    order_result = await db.execute(select(Order).where(Order.id == payload.order_id))
    order = order_result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    payment = Payment(
        order_id=payload.order_id,
        payment_method=payload.payment_method,
        amount=float(payload.amount),
    )
    db.add(payment)

    # Auto-mark the order as completed
    order.payment_status = "completed"
    await db.flush()
    return payment


# ── Sync: offline orders ─────────────────────────────────────────────────

@router.post(
    "/sync/orders",
    response_model=SyncResponse,
    summary="Bulk-sync orders from an offline POS device",
)
async def api_sync_orders(
    payload: SyncOrdersRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await sync_orders(db, payload.orders)


# ── Sync: offline payments ───────────────────────────────────────────────

@router.post(
    "/sync/payments",
    response_model=SyncResponse,
    summary="Bulk-sync payments from an offline POS device",
)
async def api_sync_payments(
    payload: SyncPaymentsRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await sync_payments(db, payload.payments)
