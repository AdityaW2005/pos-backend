"""
Analytics routes – dashboard data endpoints.

All amounts are scoped to a single store and an optional date range.

GET /analytics/summary → full dashboard summary
"""

from datetime import date, datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.orders import Order, Payment
from app.models.users import User
from app.schemas.order_schema import AnalyticsSummary
from app.utils.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/summary",
    response_model=AnalyticsSummary,
    summary="Dashboard analytics summary for a store",
)
async def get_summary(
    store_id: UUID = Query(...),
    start_date: date | None = Query(None, description="Inclusive start date (YYYY-MM-DD)"),
    end_date: date | None = Query(None, description="Inclusive end date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Returns aggregated financial metrics for the dashboard:

    - total_revenue (net_amount of completed orders)
    - total_orders
    - tax_collected
    - gross_sales
    - net_sales
    - total_discounts
    - payment_breakdown (cash / card / upi)
    """

    # ── Base filter ───────────────────────────────────────────────────────
    filters = [
        Order.store_id == store_id,
        Order.payment_status == "completed",
    ]
    if start_date:
        filters.append(
            Order.created_at >= datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc)
        )
    if end_date:
        # end of the day
        filters.append(
            Order.created_at < datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59, tzinfo=timezone.utc)
        )

    # ── Order aggregates ──────────────────────────────────────────────────
    order_q = select(
        func.coalesce(func.sum(Order.net_amount), 0).label("total_revenue"),
        func.count(Order.id).label("total_orders"),
        func.coalesce(func.sum(Order.tax_amount), 0).label("tax_collected"),
        func.coalesce(func.sum(Order.gross_amount), 0).label("gross_sales"),
        func.coalesce(func.sum(Order.net_amount), 0).label("net_sales"),
        func.coalesce(func.sum(Order.discount_amount), 0).label("total_discounts"),
    ).where(*filters)

    result = await db.execute(order_q)
    row = result.one()

    # ── Payment breakdown ─────────────────────────────────────────────────
    pay_q = (
        select(
            func.coalesce(
                func.sum(case((Payment.payment_method == "cash", Payment.amount), else_=0)), 0
            ).label("cash"),
            func.coalesce(
                func.sum(case((Payment.payment_method == "card", Payment.amount), else_=0)), 0
            ).label("card"),
            func.coalesce(
                func.sum(case((Payment.payment_method == "upi", Payment.amount), else_=0)), 0
            ).label("upi"),
        )
        .join(Order, Payment.order_id == Order.id)
        .where(*filters)
    )

    pay_result = await db.execute(pay_q)
    pay_row = pay_result.one()

    return AnalyticsSummary(
        total_revenue=float(row.total_revenue),
        total_orders=int(row.total_orders),
        tax_collected=float(row.tax_collected),
        gross_sales=float(row.gross_sales),
        net_sales=float(row.net_sales),
        total_discounts=float(row.total_discounts),
        payment_breakdown={
            "cash": float(pay_row.cash),
            "card": float(pay_row.card),
            "upi": float(pay_row.upi),
        },
    )
