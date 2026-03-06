"""
Order service – encapsulates order creation business logic.

Calculates totals (gross, tax, net) from line items and
creates the Order + OrderItem rows inside a single transaction.
"""

import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orders import Order, OrderItem
from app.models.products import Product
from app.schemas.order_schema import OrderCreate


async def create_order(db: AsyncSession, payload: OrderCreate) -> Order:
    """
    Build an Order from the given payload.

    1. Resolve each product to get its tax_percent.
    2. Compute per-item totals and aggregate.
    3. Persist Order + OrderItems.
    """
    order_id = uuid.uuid4()
    gross = Decimal("0")
    tax = Decimal("0")
    items: list[OrderItem] = []

    for item in payload.items:
        # Fetch product for tax calculation
        result = await db.execute(select(Product).where(Product.id == item.product_id))
        product = result.scalar_one_or_none()
        tax_pct = Decimal(str(product.tax_percent)) if product else Decimal("0")

        item_total = Decimal(str(item.price)) * item.quantity
        item_tax = item_total * tax_pct / Decimal("100")
        gross += item_total
        tax += item_tax

        items.append(
            OrderItem(
                id=uuid.uuid4(),
                order_id=order_id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=float(item.price),
                total=float(item_total),
            )
        )

    discount = Decimal(str(payload.discount_amount))
    net = gross + tax - discount

    order = Order(
        id=order_id,
        store_id=payload.store_id,
        employee_id=payload.employee_id,
        terminal_id=payload.terminal_id,
        table_id=payload.table_id,
        order_type=payload.order_type,
        gross_amount=float(gross),
        tax_amount=float(tax),
        discount_amount=float(discount),
        net_amount=float(net),
        payment_status="pending",
    )

    db.add(order)
    db.add_all(items)
    await db.flush()  # ensure IDs are populated before returning
    return order
