"""Initial migration - Create rooms and sessions tables.

Revision ID: 001
Revises:
Create Date: 2026-02-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create rooms table
    op.create_table(
        "rooms",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("room_id", sa.String(length=8), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rooms_room_id"), "rooms", ["room_id"], unique=True)

    # Create sessions table
    op.create_table(
        "sessions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("room_id", sa.String(length=8), nullable=False),
        sa.Column("client_id", sa.String(length=100), nullable=False),
        sa.Column("client_type", sa.String(length=10), nullable=False),
        sa.Column(
            "connected_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("disconnected_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["room_id"], ["rooms.room_id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sessions_room_id"), "sessions", ["room_id"], unique=False)
    op.create_index(op.f("ix_sessions_client_id"), "sessions", ["client_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_sessions_client_id"), table_name="sessions")
    op.drop_index(op.f("ix_sessions_room_id"), table_name="sessions")
    op.drop_table("sessions")
    op.drop_index(op.f("ix_rooms_room_id"), table_name="rooms")
    op.drop_table("rooms")
