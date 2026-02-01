"""Session model for tracking client connections."""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from ..database import Base


class Session(Base):
    """Session model for tracking client connections.

    Tracks which clients (mobile/PC) are connected to which rooms.
    """

    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    room_id: Mapped[str] = mapped_column(String(8), ForeignKey("rooms.room_id"), index=True, nullable=False)
    client_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    client_type: Mapped[str] = mapped_column(String(10), nullable=False)  # "mobile" or "pc"
    connected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    disconnected_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
