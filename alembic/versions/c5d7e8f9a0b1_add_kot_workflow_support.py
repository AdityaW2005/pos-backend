"""add kot workflow support

Revision ID: c5d7e8f9a0b1
Revises: b4c9d1e2f3a4
Create Date: 2026-03-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "c5d7e8f9a0b1"
down_revision = "b4c9d1e2f3a4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Change kots.kot_number from VARCHAR(30) to INTEGER
    op.alter_column(
        "kots",
        "kot_number",
        existing_type=sa.String(30),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="kot_number::integer",
    )

    # Update kots.status default from 'printed' to 'pending'
    op.alter_column(
        "kots",
        "status",
        existing_type=sa.String(20),
        server_default="pending",
    )

    # Update orders.status default from 'new' to 'open'
    op.alter_column(
        "orders",
        "status",
        existing_type=sa.String(20),
        server_default="open",
    )


def downgrade() -> None:
    # Revert orders.status default
    op.alter_column(
        "orders",
        "status",
        existing_type=sa.String(20),
        server_default="new",
    )

    # Revert kots.status default
    op.alter_column(
        "kots",
        "status",
        existing_type=sa.String(20),
        server_default="printed",
    )

    # Revert kots.kot_number from INTEGER back to VARCHAR(30)
    op.alter_column(
        "kots",
        "kot_number",
        existing_type=sa.Integer(),
        type_=sa.String(30),
        existing_nullable=False,
        postgresql_using="kot_number::varchar",
    )
