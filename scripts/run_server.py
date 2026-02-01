#!/usr/bin/env python3
"""
Air Guitar Left Hand - Python Signaling Server Entry Point

This script starts the Python signaling server for the Air Guitar Left Hand app.
Run with: python scripts/run_server.py

Environment variables:
    SERVER_HOST: Host to bind to (default: 0.0.0.0)
    SERVER_PORT: Port to bind to (default: 3000)
    ALLOWED_ORIGINS: Comma-separated list of allowed CORS origins
    LOG_LEVEL: Logging level (default: info)
"""

import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    import uvicorn

    # Load config
    from server.python.config import config

    uvicorn.run(
        "server.python.main:app",
        host=config.HOST,
        port=config.PORT,
        log_level=config.LOG_LEVEL,
        ws_ping_interval=config.WS_PING_INTERVAL,
        ws_ping_timeout=config.WS_PING_TIMEOUT,
    )
