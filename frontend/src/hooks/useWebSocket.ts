"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import {
  WebSocketClient,
  createWebSocketClient,
  ConnectionState,
  SyncEventData,
  NotificationEventData,
} from "@/lib/websocket";
import { useAuth } from "./useAuth";
import { getAuthToken } from "@/lib/auth-client";

interface UseWebSocketOptions {
  /** Whether to enable the WebSocket connection */
  enabled?: boolean;
  /** Callback for sync events */
  onSyncEvent?: (data: SyncEventData) => void;
  /** Callback for notification events */
  onNotification?: (data: NotificationEventData) => void;
}

interface UseWebSocketReturn {
  /** Current connection state */
  connectionState: ConnectionState;
  /** Whether connected */
  isConnected: boolean;
  /** Connect to WebSocket */
  connect: () => void;
  /** Disconnect from WebSocket */
  disconnect: () => void;
  /** Last error message */
  lastError: string | null;
}

/**
 * Hook for managing WebSocket connection for real-time sync.
 *
 * Features:
 * - Automatic connection when authenticated
 * - Automatic reconnection on disconnect
 * - Sync event handling for tasks/tags/reminders
 * - Notification delivery
 *
 * @example
 * ```tsx
 * const { connectionState, isConnected } = useWebSocket({
 *   onSyncEvent: (data) => {
 *     if (data.entity_type === 'task') {
 *       // Update task state
 *       refreshTasks();
 *     }
 *   },
 *   onNotification: (data) => {
 *     showToast(data.title, data.body);
 *   },
 * });
 * ```
 */
export function useWebSocket(
  options: UseWebSocketOptions = {}
): UseWebSocketReturn {
  const { enabled = true, onSyncEvent, onNotification } = options;
  const { isAuthenticated } = useAuth();
  const [token, setToken] = useState<string | null>(null);

  const [connectionState, setConnectionState] =
    useState<ConnectionState>("disconnected");
  const [lastError, setLastError] = useState<string | null>(null);

  const clientRef = useRef<WebSocketClient | null>(null);
  const onSyncEventRef = useRef(onSyncEvent);
  const onNotificationRef = useRef(onNotification);

  // Keep callback refs up to date
  useEffect(() => {
    onSyncEventRef.current = onSyncEvent;
    onNotificationRef.current = onNotification;
  }, [onSyncEvent, onNotification]);

  // Fetch token when authenticated
  useEffect(() => {
    if (isAuthenticated) {
      getAuthToken().then(setToken);
    } else {
      setToken(null);
    }
  }, [isAuthenticated]);

  const connect = useCallback(() => {
    if (!token || clientRef.current?.isConnected()) {
      return;
    }

    // Create new client
    clientRef.current = createWebSocketClient({
      token,
      baseUrl: process.env.NEXT_PUBLIC_WS_URL,
      onStateChange: setConnectionState,
      onSyncEvent: (data) => onSyncEventRef.current?.(data),
      onNotification: (data) => onNotificationRef.current?.(data),
      onError: (error) => setLastError(error.message),
    });

    clientRef.current.connect();
  }, [token]);

  const disconnect = useCallback(() => {
    clientRef.current?.disconnect();
    clientRef.current = null;
  }, []);

  // Connect when authenticated and enabled
  useEffect(() => {
    if (enabled && isAuthenticated && token) {
      connect();
    } else {
      disconnect();
    }

    return () => {
      disconnect();
    };
  }, [enabled, isAuthenticated, token, connect, disconnect]);

  // Update token when it changes
  useEffect(() => {
    if (token && clientRef.current) {
      clientRef.current.updateToken(token);
    }
  }, [token]);

  return {
    connectionState,
    isConnected: connectionState === "connected",
    connect,
    disconnect,
    lastError,
  };
}

/**
 * Hook for subscribing to task sync events.
 *
 * Provides callbacks for task create/update/delete operations
 * to keep local state in sync with server changes.
 */
export function useTaskSync(callbacks: {
  onTaskCreated?: (task: Record<string, unknown>) => void;
  onTaskUpdated?: (task: Record<string, unknown>) => void;
  onTaskDeleted?: (taskId: string) => void;
}) {
  const { onTaskCreated, onTaskUpdated, onTaskDeleted } = callbacks;

  const handleSyncEvent = useCallback(
    (data: SyncEventData) => {
      if (data.entity_type !== "task") return;

      switch (data.operation) {
        case "create":
          onTaskCreated?.(data.payload);
          break;
        case "update":
          onTaskUpdated?.(data.payload);
          break;
        case "delete":
          onTaskDeleted?.(data.entity_id);
          break;
      }
    },
    [onTaskCreated, onTaskUpdated, onTaskDeleted]
  );

  return useWebSocket({
    onSyncEvent: handleSyncEvent,
  });
}

/**
 * Hook for receiving real-time notifications.
 */
export function useRealtimeNotifications(
  onNotification: (data: NotificationEventData) => void
) {
  return useWebSocket({
    onNotification,
  });
}
