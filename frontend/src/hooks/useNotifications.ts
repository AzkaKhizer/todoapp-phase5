"use client";

import { useState, useCallback, useEffect } from "react";
import type { Notification } from "@/lib/types";

const MAX_NOTIFICATIONS = 5;

interface UseNotificationsOptions {
  maxNotifications?: number;
}

export function useNotifications(options: UseNotificationsOptions = {}) {
  const { maxNotifications = MAX_NOTIFICATIONS } = options;
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const addNotification = useCallback(
    (notification: Omit<Notification, "id" | "timestamp">) => {
      const newNotification: Notification = {
        ...notification,
        id: `notification-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
        timestamp: new Date().toISOString(),
      };

      setNotifications((prev) => {
        const updated = [newNotification, ...prev];
        return updated.slice(0, maxNotifications);
      });

      return newNotification.id;
    },
    [maxNotifications]
  );

  const dismissNotification = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  const clearAll = useCallback(() => {
    setNotifications([]);
  }, []);

  // Convenience methods for different notification types
  const showReminder = useCallback(
    (title: string, body: string, action_url?: string) => {
      return addNotification({
        type: "reminder",
        title,
        body,
        action_url,
      });
    },
    [addNotification]
  );

  const showSuccess = useCallback(
    (title: string, body: string) => {
      return addNotification({
        type: "success",
        title,
        body,
      });
    },
    [addNotification]
  );

  const showError = useCallback(
    (title: string, body: string) => {
      return addNotification({
        type: "error",
        title,
        body,
      });
    },
    [addNotification]
  );

  const showInfo = useCallback(
    (title: string, body: string, action_url?: string) => {
      return addNotification({
        type: "info",
        title,
        body,
        action_url,
      });
    },
    [addNotification]
  );

  return {
    notifications,
    addNotification,
    dismissNotification,
    clearAll,
    showReminder,
    showSuccess,
    showError,
    showInfo,
  };
}

// WebSocket-based notification listener for real-time reminders
interface WebSocketNotificationOptions {
  enabled: boolean;
  token?: string;
  onNotification?: (notification: Notification) => void;
}

export function useWebSocketNotifications({
  enabled,
  token,
  onNotification,
}: WebSocketNotificationOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastError, setLastError] = useState<string | null>(null);

  useEffect(() => {
    if (!enabled || !token) return;

    let ws: WebSocket | null = null;
    let reconnectTimeout: NodeJS.Timeout | null = null;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;
    const baseReconnectDelay = 1000;

    const connect = () => {
      try {
        const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";
        ws = new WebSocket(`${wsUrl}/ws/notifications?token=${token}`);

        ws.onopen = () => {
          setIsConnected(true);
          setLastError(null);
          reconnectAttempts = 0;
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);

            // Handle different message types
            if (data.type === "notification" && data.data) {
              const notification: Notification = {
                id: data.data.notification_id || `ws-${Date.now()}`,
                type: "reminder",
                title: data.data.title,
                body: data.data.body,
                action_url: data.data.action_url,
                timestamp: new Date().toISOString(),
              };
              onNotification?.(notification);
            }
          } catch {
            // Ignore parse errors for non-JSON messages
          }
        };

        ws.onclose = () => {
          setIsConnected(false);

          // Attempt reconnection with exponential backoff
          if (reconnectAttempts < maxReconnectAttempts) {
            const delay = baseReconnectDelay * Math.pow(2, reconnectAttempts);
            reconnectAttempts++;
            reconnectTimeout = setTimeout(connect, delay);
          }
        };

        ws.onerror = () => {
          setLastError("WebSocket connection error");
        };
      } catch (error) {
        setLastError("Failed to establish WebSocket connection");
      }
    };

    connect();

    return () => {
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
      if (ws) {
        ws.close();
      }
    };
  }, [enabled, token, onNotification]);

  return {
    isConnected,
    lastError,
  };
}
