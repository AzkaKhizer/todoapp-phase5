/**
 * WebSocket client for real-time task synchronization.
 *
 * Features:
 * - Automatic reconnection with exponential backoff
 * - JWT authentication
 * - Message type handling
 * - Connection state management
 */

export type WebSocketMessageType =
  | "connected"
  | "sync"
  | "notification"
  | "ping"
  | "pong"
  | "error";

export interface WebSocketMessage<T = unknown> {
  type: WebSocketMessageType;
  data: T;
}

export interface SyncEventData {
  entity_type: "task" | "tag" | "reminder";
  entity_id: string;
  operation: "create" | "update" | "delete";
  payload: Record<string, unknown>;
  timestamp: string;
}

export interface NotificationEventData {
  title: string;
  body: string;
  notification_type: "info" | "success" | "error" | "reminder";
  action_url?: string;
  timestamp: string;
}

export type ConnectionState =
  | "connecting"
  | "connected"
  | "disconnected"
  | "reconnecting";

export interface WebSocketClientOptions {
  /** Base URL for WebSocket connection (defaults to window.location) */
  baseUrl?: string;
  /** JWT token for authentication */
  token: string;
  /** Maximum reconnection attempts (default: 5) */
  maxReconnectAttempts?: number;
  /** Base delay between reconnection attempts in ms (default: 1000) */
  reconnectBaseDelay?: number;
  /** Ping interval in ms (default: 30000) */
  pingInterval?: number;
  /** Callback for sync events */
  onSyncEvent?: (data: SyncEventData) => void;
  /** Callback for notification events */
  onNotification?: (data: NotificationEventData) => void;
  /** Callback for connection state changes */
  onStateChange?: (state: ConnectionState) => void;
  /** Callback for errors */
  onError?: (error: Error) => void;
}

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private options: Required<WebSocketClientOptions>;
  private reconnectAttempts = 0;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private pingInterval: NodeJS.Timeout | null = null;
  private state: ConnectionState = "disconnected";

  constructor(options: WebSocketClientOptions) {
    this.options = {
      baseUrl: options.baseUrl || this.getDefaultBaseUrl(),
      token: options.token,
      maxReconnectAttempts: options.maxReconnectAttempts ?? 5,
      reconnectBaseDelay: options.reconnectBaseDelay ?? 1000,
      pingInterval: options.pingInterval ?? 30000,
      onSyncEvent: options.onSyncEvent ?? (() => {}),
      onNotification: options.onNotification ?? (() => {}),
      onStateChange: options.onStateChange ?? (() => {}),
      onError: options.onError ?? (() => {}),
    };
  }

  private getDefaultBaseUrl(): string {
    if (typeof window === "undefined") {
      return "ws://localhost:8000";
    }
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${window.location.host}`;
  }

  /**
   * Connect to the WebSocket server.
   */
  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    this.setState("connecting");

    const url = `${this.options.baseUrl}/ws/sync?token=${encodeURIComponent(
      this.options.token
    )}`;

    try {
      this.ws = new WebSocket(url);
      this.setupEventHandlers();
    } catch (error) {
      this.handleError(error as Error);
      this.scheduleReconnect();
    }
  }

  /**
   * Disconnect from the WebSocket server.
   */
  disconnect(): void {
    this.clearTimers();
    this.reconnectAttempts = this.options.maxReconnectAttempts; // Prevent reconnection

    if (this.ws) {
      this.ws.close(1000, "Client disconnect");
      this.ws = null;
    }

    this.setState("disconnected");
  }

  /**
   * Send a message to the server.
   */
  send(type: string, data?: unknown): boolean {
    if (this.ws?.readyState !== WebSocket.OPEN) {
      return false;
    }

    try {
      this.ws.send(JSON.stringify({ type, data }));
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Send a ping to keep the connection alive.
   */
  ping(): boolean {
    return this.send("ping", { timestamp: new Date().toISOString() });
  }

  /**
   * Get the current connection state.
   */
  getState(): ConnectionState {
    return this.state;
  }

  /**
   * Check if connected.
   */
  isConnected(): boolean {
    return this.state === "connected" && this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * Update the authentication token.
   */
  updateToken(token: string): void {
    this.options.token = token;
    if (this.isConnected()) {
      // Reconnect with new token
      this.disconnect();
      this.reconnectAttempts = 0;
      this.connect();
    }
  }

  private setupEventHandlers(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      this.reconnectAttempts = 0;
      this.setState("connected");
      this.startPingInterval();
    };

    this.ws.onclose = (event) => {
      this.clearTimers();

      if (event.code === 1000) {
        // Normal closure
        this.setState("disconnected");
      } else if (event.code === 4001) {
        // Authentication error
        this.handleError(new Error("Authentication failed"));
        this.setState("disconnected");
      } else {
        // Unexpected closure, try to reconnect
        this.scheduleReconnect();
      }
    };

    this.ws.onerror = () => {
      this.handleError(new Error("WebSocket connection error"));
    };

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as WebSocketMessage;
        this.handleMessage(message);
      } catch {
        // Ignore parse errors
      }
    };
  }

  private handleMessage(message: WebSocketMessage): void {
    switch (message.type) {
      case "connected":
        // Already handled in onopen
        break;

      case "sync":
        this.options.onSyncEvent(message.data as SyncEventData);
        break;

      case "notification":
        this.options.onNotification(message.data as NotificationEventData);
        break;

      case "ping":
        this.send("pong", { timestamp: new Date().toISOString() });
        break;

      case "pong":
        // Server responded to our ping
        break;

      case "error":
        this.handleError(
          new Error((message.data as { message?: string })?.message || "Unknown error")
        );
        break;
    }
  }

  private setState(state: ConnectionState): void {
    if (this.state !== state) {
      this.state = state;
      this.options.onStateChange(state);
    }
  }

  private handleError(error: Error): void {
    this.options.onError(error);
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.options.maxReconnectAttempts) {
      this.setState("disconnected");
      return;
    }

    this.setState("reconnecting");
    this.reconnectAttempts++;

    const delay =
      this.options.reconnectBaseDelay * Math.pow(2, this.reconnectAttempts - 1);

    this.reconnectTimeout = setTimeout(() => {
      this.connect();
    }, delay);
  }

  private startPingInterval(): void {
    this.pingInterval = setInterval(() => {
      this.ping();
    }, this.options.pingInterval);
  }

  private clearTimers(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }
}

/**
 * Create a WebSocket client instance.
 */
export function createWebSocketClient(
  options: WebSocketClientOptions
): WebSocketClient {
  return new WebSocketClient(options);
}
