"""
Delivery Zone models – zone-based delivery management.

- Zone: a delivery zone definition.
- ZoneStoreLink: links zones to stores (many-to-many).
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Index, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Zone(Base):
    __tablename__ = "zones"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # dine_in | delivery | takeaway
    sub_order_type: Mapped[str] = mapped_column(String(50), nullable=False, default="delivery")
    # Delivery fee for this zone
    delivery_fee: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    min_order_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    # Polygon/boundary data as GeoJSON or coordinate list
    boundary: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    store_links = relationship("ZoneStoreLink", back_populates="zone", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_zones_owner_id", "owner_id"),
    )


class ZoneStoreLink(Base):
    __tablename__ = "zone_store_links"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    zone_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("zones.id", ondelete="CASCADE"), nullable=False
    )
    store_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False
    )

    zone = relationship("Zone", back_populates="store_links")

    __table_args__ = (
        Index("ix_zone_store_links_zone_id", "zone_id"),
        Index("ix_zone_store_links_store_id", "store_id"),
        Index("ix_zone_store_links_unique", "zone_id", "store_id", unique=True),
    )
