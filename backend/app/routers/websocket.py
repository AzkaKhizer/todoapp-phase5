"""WebSocket router for real-time sync.

This router provides WebSocket endpoints for:
- Real-time task sync across browser tabs/devices
- Push notifications for reminders
- Connection status and heartbeat
"""

import logging
from typing import Any

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.services.auth import get_user_id_from_token, verify_token
from app.services.websocket_manager import get_websocket_manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/sync")
async def websocket_sync(
    websocket: WebSocket,
    token: str = Query(..., description="JWT authentication token"),
) -> None:
    """WebSocket endpoint for real-time task synchronization.

    Clients connect with their JWT token and receive:
    - Task create/update/delete events
    - Reminder notifications
    - Connection status updates

    Message format (JSON):
    {
        "type": "sync" | "notification" | "connected" | "ping" | "pong",
        "data": { ... }
    }

    Sync event data:
    {
        "entity_type": "task" | "tag" | "reminder",
        "entity_id": "uuid",
        "operation": "create" | "update" | "delete",
        "payload": { ... entity data ... },
        "timestamp": "ISO datetime"
    }
    """
    manager = get_websocket_manager()

    # Authenticate the connection
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=4001, reason="Invalid token: missing user ID")
            return
    except Exception as e:
        logger.warning(f"WebSocket authentication failed: {e}")
        await websocket.close(code=4001, reason="Authentication failed")
        return

    # Register the connection
    connection = await manager.connect(websocket, user_id)

    try:
        # Keep the connection alive and handle messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_json()
                await handle_client_message(websocket, user_id, data, manager)
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                # Send error back to client
                try:
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": str(e)},
                    })
                except Exception:
                    break
    finally:
        # Clean up connection
        await manager.disconnect(websocket, user_id)


@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(..., description="JWT authentication token"),
) -> None:
    """WebSocket endpoint for push notifications only.

    Lighter-weight connection for receiving notifications without full sync.
    Useful for mobile clients or background tabs.

    Message format (JSON):
    {
        "type": "notification",
        "data": {
            "title": "...",
            "body": "...",
            "notification_type": "reminder" | "info" | "success" | "error",
            "action_url": "..." (optional),
            "timestamp": "ISO datetime"
        }
    }
    """
    manager = get_websocket_manager()

    # Authenticate
    try:
        user_id = get_user_id_from_token(token)
    except Exception as e:
        logger.warning(f"WebSocket notification auth failed: {e}")
        await websocket.close(code=4001, reason="Authentication failed")
        return

    # Register connection
    await manager.connect(websocket, user_id)

    try:
        while True:
            try:
                data = await websocket.receive_json()
                await handle_client_message(websocket, user_id, data, manager)
            except WebSocketDisconnect:
                break
            except Exception:
                break
    finally:
        await manager.disconnect(websocket, user_id)


async def handle_client_message(
    websocket: WebSocket,
    user_id: str,
    data: dict[str, Any],
    manager: Any,
) -> None:
    """Handle incoming messages from WebSocket clients.

    Supported message types:
    - ping: Heartbeat check, responds with pong
    - pong: Response to server ping
    - subscribe: Subscribe to specific entity updates (future)
    - unsubscribe: Unsubscribe from entity updates (future)
    """
    message_type = data.get("type", "")

    if message_type == "ping":
        # Respond to client ping with pong
        await websocket.send_json({
            "type": "pong",
            "data": {"timestamp": data.get("data", {}).get("timestamp")},
        })
        await manager.update_ping(websocket, user_id)

    elif message_type == "pong":
        # Update last ping time
        await manager.update_ping(websocket, user_id)

    elif message_type == "subscribe":
        # Future: Subscribe to specific entity updates
        logger.debug(f"Subscribe request from {user_id}: {data}")

    elif message_type == "unsubscribe":
        # Future: Unsubscribe from entity updates
        logger.debug(f"Unsubscribe request from {user_id}: {data}")

    else:
        logger.warning(f"Unknown message type from {user_id}: {message_type}")


# Health check endpoint for WebSocket status
@router.get("/ws/status")
async def websocket_status() -> dict[str, Any]:
    """Get WebSocket connection status.

    Returns:
        Connection statistics
    """
    manager = get_websocket_manager()
    return {
        "total_connections": manager.get_total_connections(),
        "connected_users": len(manager.get_connected_users()),
    }
