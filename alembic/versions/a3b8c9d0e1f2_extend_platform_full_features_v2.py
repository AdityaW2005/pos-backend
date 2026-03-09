"""extend platform full features v2

Revision ID: a3b8c9d0e1f2
Revises: f29df2f97962
Create Date: 2026-03-08 00:00:00.000000

New tables:
- notifications
- device_tokens
- zones
- zone_store_links
- permission_groups
- permission_group_members
- permission_group_stores
- report_templates
- report_runs
- integration_logs

Altered tables:
- users: add created_by_id column
- stores: add state, city, outlet_type columns
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "a3b8c9d0e1f2"
down_revision = "f29df2f97962"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── users: add created_by_id ──────────────────────────────────────────
    op.add_column("users", sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_users_created_by", "users", "users", ["created_by_id"], ["id"], ondelete="SET NULL")
    op.create_index("ix_users_created_by", "users", ["created_by_id"])

    # ── stores: add state, city, outlet_type ──────────────────────────────
    op.add_column("stores", sa.Column("state", sa.String(100), nullable=True))
    op.add_column("stores", sa.Column("city", sa.String(100), nullable=True))
    op.add_column("stores", sa.Column("outlet_type", sa.String(20), nullable=True))

    # ── notifications ─────────────────────────────────────────────────────
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stores.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.Text, nullable=True),
        sa.Column("category", sa.String(50), nullable=False, server_default="system"),
        sa.Column("entity_type", sa.String(50), nullable=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_read", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("data", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_store_id", "notifications", ["store_id"])
    op.create_index("ix_notifications_is_read", "notifications", ["is_read"])
    op.create_index("ix_notifications_created_at", "notifications", ["created_at"])

    # ── device_tokens ─────────────────────────────────────────────────────
    op.create_table(
        "device_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("platform", sa.String(20), nullable=False),
        sa.Column("token", sa.String(500), nullable=False),
        sa.Column("device_name", sa.String(120), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_device_tokens_user_id", "device_tokens", ["user_id"])
    op.create_index("ix_device_tokens_token", "device_tokens", ["token"], unique=True)

    # ── zones ─────────────────────────────────────────────────────────────
    op.create_table(
        "zones",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("sub_order_type", sa.String(50), nullable=False, server_default="delivery"),
        sa.Column("delivery_fee", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("min_order_amount", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("boundary", postgresql.JSONB, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_zones_owner_id", "zones", ["owner_id"])

    # ── zone_store_links ──────────────────────────────────────────────────
    op.create_table(
        "zone_store_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("zone_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("zones.id", ondelete="CASCADE"), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stores.id", ondelete="CASCADE"), nullable=False),
    )
    op.create_index("ix_zone_store_links_zone_id", "zone_store_links", ["zone_id"])
    op.create_index("ix_zone_store_links_store_id", "zone_store_links", ["store_id"])
    op.create_index("ix_zone_store_links_unique", "zone_store_links", ["zone_id", "store_id"], unique=True)

    # ── permission_groups ─────────────────────────────────────────────────
    op.create_table(
        "permission_groups",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("group_type", sa.String(50), nullable=False, server_default="admin"),
        sa.Column("permissions", postgresql.JSONB, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_permission_groups_owner_id", "permission_groups", ["owner_id"])
    op.create_index("ix_permission_groups_type", "permission_groups", ["group_type"])

    # ── permission_group_members ──────────────────────────────────────────
    op.create_table(
        "permission_group_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("permission_groups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    )
    op.create_index("ix_pgm_group_id", "permission_group_members", ["group_id"])
    op.create_index("ix_pgm_user_id", "permission_group_members", ["user_id"])
    op.create_index("ix_pgm_unique", "permission_group_members", ["group_id", "user_id"], unique=True)

    # ── permission_group_stores ───────────────────────────────────────────
    op.create_table(
        "permission_group_stores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("permission_groups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stores.id", ondelete="CASCADE"), nullable=False),
    )
    op.create_index("ix_pgs_group_id", "permission_group_stores", ["group_id"])
    op.create_index("ix_pgs_store_id", "permission_group_stores", ["store_id"])
    op.create_index("ix_pgs_unique", "permission_group_stores", ["group_id", "store_id"], unique=True)

    # ── report_templates ──────────────────────────────────────────────────
    op.create_table(
        "report_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(100), unique=True, nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("category", sa.String(50), nullable=False, server_default="sales"),
        sa.Column("parameters_schema", postgresql.JSONB, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── report_runs ───────────────────────────────────────────────────────
    op.create_table(
        "report_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("report_templates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stores.id", ondelete="CASCADE"), nullable=False),
        sa.Column("requested_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("parameters", postgresql.JSONB, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("result", postgresql.JSONB, nullable=True),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_report_runs_template_id", "report_runs", ["template_id"])
    op.create_index("ix_report_runs_store_id", "report_runs", ["store_id"])
    op.create_index("ix_report_runs_requested_by", "report_runs", ["requested_by"])
    op.create_index("ix_report_runs_status", "report_runs", ["status"])

    # ── integration_logs ──────────────────────────────────────────────────
    op.create_table(
        "integration_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("stores.id", ondelete="CASCADE"), nullable=False),
        sa.Column("aggregator_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("aggregator_configs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("log_type", sa.String(50), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="success"),
        sa.Column("entity_type", sa.String(50), nullable=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("details", postgresql.JSONB, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_integration_logs_store_id", "integration_logs", ["store_id"])
    op.create_index("ix_integration_logs_type", "integration_logs", ["log_type"])
    op.create_index("ix_integration_logs_aggregator_id", "integration_logs", ["aggregator_id"])
    op.create_index("ix_integration_logs_created_at", "integration_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("integration_logs")
    op.drop_table("report_runs")
    op.drop_table("report_templates")
    op.drop_table("permission_group_stores")
    op.drop_table("permission_group_members")
    op.drop_table("permission_groups")
    op.drop_table("zone_store_links")
    op.drop_table("zones")
    op.drop_table("device_tokens")
    op.drop_table("notifications")
    op.drop_column("stores", "outlet_type")
    op.drop_column("stores", "city")
    op.drop_column("stores", "state")
    op.drop_index("ix_users_created_by", table_name="users")
    op.drop_constraint("fk_users_created_by", "users", type_="foreignkey")
    op.drop_column("users", "created_by_id")
