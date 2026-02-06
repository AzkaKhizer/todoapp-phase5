"""WebSocket connection manager for real-time sync.

This service manages WebSocket connections and broadcasts events to connected clients.
Each user can have multiple connections (multiple browser tabs/devices).
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import WebSocket

logger = logging.getLogger(__name__)


@dataclass
class ConnectionInfo:
    """Information about a WebSocket connection."""

    websocket: WebSocket
    user_id: str
    connected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_ping: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class WebSocketManager:
    """Manager for WebSocket connections and broadcasting.

    Features:
    - Multiple connections per user (multiple tabs/devices)
    - User-scoped message broadcasting
    - Connection heartbeat tracking
    - Graceful disconnection handling
    """

    def __init__(self):
        """Initialize the WebSocket manager."""
        # Map of user_id -> list of connections
        self._connections: dict[str, list[ConnectionInfo]] = {}
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, user_id: str) -> ConnectionInfo:
        """Register a new WebSocket connection.

        Args:
            websocket: The WebSocket connection
            user_id: The authenticated user ID

        Returns:
            ConnectionInfo for the new connection
        """
        await websocket.accept()

        connection = ConnectionInfo(
            websocket=websocket,
            user_id=user_id,
        )

        async with self._lock:
            if user_id not in self._connections:
                self._connections[user_id] = []
            self._connections[user_id].append(connection)

        logger.info(
            f"WebSocket connected: user={user_id}, "
            f"total_connections={self.get_connection_count(user_id)}"
        )

        # Send welcome message
        await self._send_message(
            websocket,
            {
                "type": "connected",
                "data": {
                    "message": "Connected to real-time sync",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            },
        )

        return connection

    async def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        """Remove a WebSocket connection.

        Args:
            websocket: The WebSocket connection to remove
            user_id: The user ID
        """
        async with self._lock:
            if user_id in self._connections:
                self._connections[user_id] = [
                    conn
                    for conn in self._connections[user_id]
                    if conn.websocket != websocket
                ]
                # Clean up empty user entries
                if not self._connections[user_id]:
                    del self._connections[user_id]

        logger.info(
            f"WebSocket disconnected: user={user_id}, "
            f"remaining_connections={self.get_connection_count(user_id)}"
        )

    async def broadcast_to_user(
        self,
        user_id: str,
        message: dict[str, Any],
    ) -> int:
        """Broadcast a message to all connections for a user.

        Args:
            user_id: The target user ID
            message: The message to broadcast

        Returns:
            Number of connections that received the message
        """
        connections = self._connections.get(user_id, [])
        if not connections:
            return 0

        sent_count = 0
        failed_connections = []

        for conn in connections:
            try:
                await self._send_message(conn.websocket, message)
                sent_count += 1
            except Exception as e:
                logger.warning(f"Failed to send to connection: {e}")
                failed_connections.append(conn)

        # Clean up failed connections
        if failed_connections:
            async with self._lock:
                for conn in failed_connections:
                    if user_id in self._connections:
                        self._connections[user_id] = [
                            c
                            for c in self._connections[user_id]
                            if c.websocket != conn.websocket
                        ]

        return sent_count

    async def broadcast_sync_event(
        self,
        user_id: str,
        entity_type: str,
        entity_id: UUID | str,
        operation: str,
        payload: dict[str, Any],
    ) -> int:
        """Broadcast a sync event to a user.

        Args:
            user_id: The target user ID
            entity_type: Type of entity (task, tag, reminder)
            entity_id: ID of the entity
            operation: Operation type (create, update, delete)
            payload: The entity data

        Returns:
            Number of connections that received the message
        """
        message = {
            "type": "sync",
            "data": {
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "operation": operation,
                "payload": payload,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }
        return await self.broadcast_to_user(user_id, message)

    async def broadcast_notification(
        self,
        user_id: str,
        title: str,
        body: str,
        notification_type: str = "info",
        action_url: str | None = None,
    ) -> int:
        """Broadcast a notification to a user.

        Args:
            user_id: The target user ID
            title: Notification title
            body: Notification body
            notification_type: Type (info, success, error, reminder)
            action_url: Optional URL for the notification action

        Returns:
            Number of connections that received the message
        """
        message = {
            "type": "notification",
            "data": {
                "title": title,
                "body": body,
                "notification_type": notification_type,
                "action_url": action_url,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }
        return await self.broadcast_to_user(user_id, message)

    async def send_ping(self, user_id: str) -> None:
        """Send a ping to all connections for a user.

        Args:
            user_id: The user ID
        """
        message = {
            "type": "ping",
            "data": {"timestamp": datetime.now(timezone.utc).isoformat()},
        }
        await self.broadcast_to_user(user_id, message)

    def get_connection_count(self, user_id: str) -> int:
        """Get the number of active connections for a user.

        Args:
            user_id: The user ID

        Returns:
            Number of active connections
        """
        return len(self._connections.get(user_id, []))

    def get_total_connections(self) -> int:
        """Get the total number of active connections.

        Returns:
            Total number of connections across all users
        """
        return sum(len(conns) for conns in self._connections.values())

    def get_connected_users(self) -> list[str]:
        """Get list of user IDs with active connections.

        Returns:
            List of user IDs
        """
        return list(self._connections.keys())

    async def update_ping(self, websocket: WebSocket, user_id: str) -> None:
        """Update the last ping time for a connection.

        Args:
            websocket: The WebSocket connection
            user_id: The user ID
        """
        connections = self._connections.get(user_id, [])
        for conn in connections:
            if conn.websocket == websocket:
                conn.last_ping = datetime.now(timezone.utc)
                break

    async def _send_message(
        self,
        websocket: WebSocket,
        message: dict[str, Any],
    ) -> None:
        """Send a message to a WebSocket connection.

        Args:
            websocket: The WebSocket connection
            message: The message to send
        """
        await websocket.send_json(message)


# Global instance
_manager: WebSocketManager | None = None


def get_websocket_manager() -> WebSocketManager:
    """Get the global WebSocket manager instance."""
    global _manager
    if _manager is None:
        _manager = WebSocketManager()
    return _manager
