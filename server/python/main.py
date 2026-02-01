"""Main FastAPI server for Air Guitar Left Hand.

This server provides:
- WebSocket relay between PC and mobile devices
- ADB (Android Debug Bridge) API endpoints
- Room management API
- Health check endpoint
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from .config import config
from .websocket import ConnectionManager, get_connection_manager
from .adb import get_adb_manager
from .database import get_db_session
from .models.room import Room

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global managers
connection_manager: ConnectionManager | None = None
adb_manager = get_adb_manager()


# Pydantic models for API
class RoomCreate(BaseModel):
    """Request model for creating a room."""

    expires_in_hours: int = 24


class RoomResponse(BaseModel):
    """Response model for room data."""

    id: int
    room_id: str
    created_at: str
    expires_at: str | None


class RoomValidateResponse(BaseModel):
    """Response model for room validation."""

    valid: bool
    room_id: str | None = None
    message: str = ""


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Lifespan context manager for startup and shutdown events."""
    global connection_manager

    # Startup
    logger.info("Starting Air Guitar Left Hand server...")

    # Initialize connection manager
    connection_manager = get_connection_manager()
    logger.info("Connection manager initialized")

    yield

    # Shutdown
    logger.info("Shutting down server...")
    if connection_manager:
        await connection_manager.disconnect_all()
    logger.info("Server shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Air Guitar Left Hand Server",
    description="WebSocket relay, ADB, and Room management server",
    version="0.3.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(
        content={
            "status": "ok",
            "service": "air-guitar-left-hand-server",
            "version": "0.3.0",
        }
    )


@app.post("/api/rooms/create")
async def create_room(
    data: RoomCreate, db: AsyncSession = Depends(get_db_session)
) -> JSONResponse:
    """Create a new room.

    Args:
        data: Room creation data
        db: Database session

    Returns:
        Created room data
    """
    try:
        room = Room.create_with_expiry(expires_in_hours=data.expires_in_hours)
        db.add(room)
        await db.commit()
        await db.refresh(room)

        return JSONResponse(
            content={
                "id": room.id,
                "room_id": room.room_id,
                "created_at": room.created_at.isoformat(),
                "expires_at": room.expires_at.isoformat() if room.expires_at else None,
            }
        )
    except Exception as e:
        logger.error(f"Failed to create room: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rooms/{room_id}")
async def get_room(
    room_id: str, db: AsyncSession = Depends(get_db_session)
) -> JSONResponse:
    """Get room by ID.

    Args:
        room_id: Room ID
        db: Database session

    Returns:
        Room data or 404
    """
    from sqlalchemy import select

    try:
        result = await db.execute(select(Room).where(Room.room_id == room_id))
        room = result.scalar_one_or_none()

        if room is None:
            raise HTTPException(status_code=404, detail="Room not found")

        return JSONResponse(
            content={
                "id": room.id,
                "room_id": room.room_id,
                "created_at": room.created_at.isoformat(),
                "expires_at": room.expires_at.isoformat() if room.expires_at else None,
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get room: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/rooms/{room_id}/validate")
async def validate_room(
    room_id: str, db: AsyncSession = Depends(get_db_session)
) -> JSONResponse:
    """Validate room ID.

    Args:
        room_id: Room ID to validate
        db: Database session

    Returns:
        Validation result
    """
    from sqlalchemy import select

    try:
        result = await db.execute(select(Room).where(Room.room_id == room_id))
        room = result.scalar_one_or_none()

        if room is None:
            return JSONResponse(
                content={"valid": False, "room_id": None, "message": "Room not found"}
            )

        if room.is_expired():
            return JSONResponse(
                content={"valid": False, "room_id": room_id, "message": "Room expired"}
            )

        return JSONResponse(
            content={"valid": True, "room_id": room_id, "message": "Room valid"}
        )
    except Exception as e:
        logger.error(f"Failed to validate room: {e}")
        return JSONResponse(
            content={"valid": False, "room_id": None, "message": str(e)}
        )


@app.get("/api/adb/devices")
async def get_adb_devices() -> JSONResponse:
    """Get list of connected ADB devices."""
    try:
        devices = await adb_manager.get_devices()
        return JSONResponse(
            content={
                "devices": [
                    {
                        "device_id": d.device_id,
                        "model": d.model,
                        "product": d.product,
                        "device": d.device,
                    }
                    for d in devices
                ]
            }
        )
    except Exception as e:
        logger.error(f"Failed to get ADB devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/adb/forward")
async def adb_forward(device_id: str, local_port: int, remote_port: int) -> JSONResponse:
    """Set up ADB port forwarding."""
    try:
        success = await adb_manager.forward_port(device_id, local_port, remote_port)
        return JSONResponse(content={"success": success})
    except Exception as e:
        logger.error(f"ADB forward failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/adb/reverse")
async def adb_reverse(device_id: str, remote_port: int, local_port: int) -> JSONResponse:
    """Set up ADB reverse port forwarding."""
    try:
        success = await adb_manager.reverse_port(device_id, remote_port, local_port)
        return JSONResponse(content={"success": success})
    except Exception as e:
        logger.error(f"ADB reverse failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/adb/screen")
async def adb_screen_capture(device_id: str) -> JSONResponse:
    """Capture device screen."""
    try:
        path = await adb_manager.screen_capture(device_id)
        return JSONResponse(content={"path": path})
    except Exception as e:
        logger.error(f"Screen capture failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/adb/shell")
async def adb_shell(device_id: str, command: str) -> JSONResponse:
    """Execute shell command on device."""
    try:
        stdout, stderr, code = await adb_manager.shell_command(device_id, command)
        return JSONResponse(
            content={"stdout": stdout, "stderr": stderr, "code": code}
        )
    except Exception as e:
        logger.error(f"Shell command failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for PC and mobile relay."""
    if connection_manager is None:
        await websocket.close(code=1011, reason="Server not initialized")
        return

    await connection_manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            await connection_manager.handle_message(websocket, data)
    except WebSocketDisconnect:
        await connection_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await connection_manager.disconnect(websocket)


@app.get("/")
async def root() -> JSONResponse:
    """Root endpoint."""
    return JSONResponse(
        content={
            "message": "Air Guitar Left Hand Server",
            "endpoints": {
                "health": "/api/health",
                "websocket": "/ws",
                "rooms": {
                    "create": "/api/rooms/create",
                    "get": "/api/rooms/{room_id}",
                    "validate": "/api/rooms/{room_id}/validate",
                },
                "adb": {
                    "devices": "/api/adb/devices",
                    "forward": "/api/adb/forward",
                    "reverse": "/api/adb/reverse",
                    "screen": "/api/adb/screen",
                    "shell": "/api/adb/shell",
                },
            },
        }
    )


def run_server() -> None:
    """Run the server using uvicorn."""
    import uvicorn

    uvicorn.run(
        "server.python.main:app",
        host=config.HOST,
        port=config.PORT,
        log_level=config.LOG_LEVEL,
        ws_ping_interval=config.WS_PING_INTERVAL,
        ws_ping_timeout=config.WS_PING_TIMEOUT,
    )


if __name__ == "__main__":
    run_server()
