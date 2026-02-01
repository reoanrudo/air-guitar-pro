"""Room model for managing connection rooms."""

import string
import random
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from ..database import Base


class Room(Base):
    """Room model for managing connection rooms.

    Rooms are used to connect mobile and PC clients via Room ID.
    """

    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    room_id: Mapped[str] = mapped_column(String(8), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    @staticmethod
    def generate_room_id(length: int = 6) -> str:
        """Generate a random room ID.

        Args:
            length: Length of room ID (default: 6)

        Returns:
            Random room ID string
        """
        # Use uppercase letters and digits, excluding confusing characters
        chars = string.ascii_uppercase + string.digits
        chars = chars.replace("0", "").replace("O", "").replace("I", "").replace("1", "")
        return "".join(random.choices(chars, k=length))

    @staticmethod
    def create_with_expiry(expires_in_hours: int = 24) -> "Room":
        """Create a new room with expiration.

        Args:
            expires_in_hours: Hours until room expires (default: 24)

        Returns:
            New Room instance
        """
        room_id = Room.generate_room_id()
        expires_at = datetime.now() + timedelta(hours=expires_in_hours)
        return Room(room_id=room_id, expires_at=expires_at)

    def is_expired(self) -> bool:
        """Check if room is expired.

        Returns:
            True if expired
        """
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
