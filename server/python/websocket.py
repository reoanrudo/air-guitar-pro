"""WebSocket relay server for PC and mobile communication.

This module handles:
- PC and mobile connection management
- Message relay between devices
- User-Agent based device detection
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


def detect_device_type(user_agent: str | None) -> str:
    """Detect device type from User-Agent header.

    Args:
        user_agent: User-Agent string from WebSocket handshake

    Returns:
        "mobile" or "pc"
    """
    if not user_agent:
        return "pc"

    user_agent_lower = user_agent.lower()

    # Mobile indicators
    mobile_keywords = [
        "mobile",
        "android",
        "iphone",
        "ipad",
        "ipod",
        "expo",
        "reactnative",
    ]

    if any(keyword in user_agent_lower for keyword in mobile_keywords):
        return "mobile"

    return "pc"


@dataclass
class ClientConnection:
    """Information about a connected client."""

    websocket: WebSocket
    client_id: str
    device_type: str  # "mobile" or "pc"
    user_agent: str | None = None


@dataclass
class ConnectionManagerState:
    """State for the connection manager."""

    mobile_connections: dict[str, ClientConnection] = field(default_factory=dict)
    pc_connections: dict[str, ClientConnection] = field(default_factory=dict)
    client_id_counter: int = 0


class ConnectionManager:
    """Manages WebSocket connections between PC and mobile devices."""

    def __init__(self) -> None:
        """Initialize the connection manager."""
        self.state = ConnectionManagerState()

    def _generate_client_id(self) -> str:
        """Generate a unique client ID.

        Returns:
            Unique client ID string
        """
        self.state.client_id_counter += 1
        return f"client_{self.state.client_id_counter}"

    async def connect(self, websocket: WebSocket) -> str:
        """Accept and register a new WebSocket connection.

        Args:
            websocket: WebSocket connection to accept

        Returns:
            Client ID assigned to the connection
        """
        await websocket.accept()

        # Detect device type
        user_agent = websocket.headers.get("user-agent")
        device_type = detect_device_type(user_agent)

        # Generate client ID
        client_id = self._generate_client_id()

        # Create connection info
        connection = ClientConnection(
            websocket=websocket,
            client_id=client_id,
            device_type=device_type,
            user_agent=user_agent,
        )

        # Store in appropriate list
        if device_type == "mobile":
            self.state.mobile_connections[client_id] = connection
            logger.info(f"Mobile device connected: {client_id}")
        else:
            self.state.pc_connections[client_id] = connection
            logger.info(f"PC connected: {client_id}")

        # Send connection confirmation
        await websocket.send_json(
            {
                "type": "connected",
                "client_id": client_id,
                "device_type": device_type,
            }
        )

        # Notify other connected clients
        await self._broadcast_connection_event(client_id, device_type, "connected")

        return client_id

    async def disconnect(self, websocket: WebSocket) -> None:
        """Disconnect a WebSocket client.

        Args:
            websocket: WebSocket connection to disconnect
        """
        # Find and remove the connection
        client_id = None
        device_type = None

        # Check mobile connections
        for cid, conn in list(self.state.mobile_connections.items()):
            if conn.websocket == websocket:
                client_id = cid
                device_type = "mobile"
                del self.state.mobile_connections[cid]
                break

        # Check PC connections
        if client_id is None:
            for cid, conn in list(self.state.pc_connections.items()):
                if conn.websocket == websocket:
                    client_id = cid
                    device_type = "pc"
                    del self.state.pc_connections[cid]
                    break

        if client_id:
            logger.info(f"{device_type.capitalize()} disconnected: {client_id}")
            # Notify other clients
            await self._broadcast_connection_event(client_id, device_type, "disconnected")

    async def disconnect_all(self) -> None:
        """Disconnect all connected clients."""
        all_connections = list(self.state.mobile_connections.values()) + list(
            self.state.pc_connections.values()
        )

        for connection in all_connections:
            try:
                await connection.websocket.close()
            except Exception as e:
                logger.error(f"Error closing connection: {e}")

        self.state.mobile_connections.clear()
        self.state.pc_connections.clear()
        logger.info("All clients disconnected")

    async def handle_message(
        self, websocket: WebSocket, data: dict[str, Any]
    ) -> None:
        """Handle a message from a client.

        Args:
            websocket: WebSocket connection that sent the message
            data: Message data (JSON dict)
        """
        msg_type = data.get("type")

        if msg_type == "ping":
            await websocket.send_json({"type": "pong"})
            return

        # Find sender info
        sender_client = None
        for conn in list(self.state.mobile_connections.values()) + list(
            self.state.pc_connections.values()
        ):
            if conn.websocket == websocket:
                sender_client = conn
                break

        if not sender_client:
            logger.warning("Received message from unknown client")
            return

        # Relay messages between devices
        if sender_client.device_type == "mobile":
            # Mobile -> PC
            await self._send_to_all_pc(data)
        else:
            # PC -> Mobile
            await self._send_to_all_mobile(data)

    async def _send_to_all_mobile(self, data: dict[str, Any]) -> None:
        """Send data to all connected mobile devices.

        Args:
            data: Data to send
        """
        for connection in list(self.state.mobile_connections.values()):
            try:
                await connection.websocket.send_json(data)
            except Exception as e:
                logger.error(f"Error sending to mobile {connection.client_id}: {e}")

    async def _send_to_all_pc(self, data: dict[str, Any]) -> None:
        """Send data to all connected PCs.

        Args:
            data: Data to send
        """
        for connection in list(self.state.pc_connections.values()):
            try:
                await connection.websocket.send_json(data)
            except Exception as e:
                logger.error(f"Error sending to PC {connection.client_id}: {e}")

    async def _broadcast_connection_event(
        self, client_id: str, device_type: str, event: str
    ) -> None:
        """Broadcast a connection event to all clients.

        Args:
            client_id: ID of the client
            device_type: Type of device ("mobile" or "pc")
            event: Event type ("connected" or "disconnected")
        """
        message = {
            "type": "connection_event",
            "client_id": client_id,
            "device_type": device_type,
            "event": event,
        }

        # Send to all clients
        await self._send_to_all_mobile(message)
        await self._send_to_all_pc(message)

    def get_connected_mobile_count(self) -> int:
        """Get count of connected mobile devices.

        Returns:
            Number of connected mobile devices
        """
        return len(self.state.mobile_connections)

    def get_connected_pc_count(self) -> int:
        """Get count of connected PCs.

        Returns:
            Number of connected PCs
        """
        return len(self.state.pc_connections)


# Global connection manager instance
_connection_manager: ConnectionManager | None = None


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance.

    Returns:
        ConnectionManager instance
    """
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager
