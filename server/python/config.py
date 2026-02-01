"""Configuration for the signaling server."""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Server configuration."""

    # Server settings
    HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("SERVER_PORT", "3000"))

    # CORS settings
    ALLOWED_ORIGINS: list[str] = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:8081,http://localhost:19006,exp://192.168.*:*"
    ).split(",")

    # WebSocket settings
    WS_PING_INTERVAL: int = int(os.getenv("WS_PING_INTERVAL", "20"))
    WS_PING_TIMEOUT: int = int(os.getenv("WS_PING_TIMEOUT", "20"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")

    # Database settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+aiomysql://root:password@localhost/air_guitar",
    )
    # Sync database URL for Alembic
    DATABASE_URL_SYNC: str = os.getenv(
        "DATABASE_URL_SYNC",
        "mysql+pymysql://root:password@localhost/air_guitar",
    )


config = Config()
