/**
 * Chat API TypeScript Contracts
 *
 * These types define the contract between frontend and backend
 * for the chat functionality. Backend is already implemented.
 */

// ============================================================
// Request Types
// ============================================================

/**
 * Request body for POST /api/chat
 */
export interface ChatRequest {
  /** User's message (1-2000 characters) */
  message: string;
  /** Optional conversation ID to continue existing conversation */
  conversation_id?: string;
}

// ============================================================
// Response Types
// ============================================================

/**
 * Response from POST /api/chat
 */
export interface ChatResponse {
  /** AI assistant's response message */
  message: string;
  /** Conversation ID (created or existing) */
  conversation_id: string;
}

/**
 * Single message in a conversation
 */
export interface Message {
  /** UUID of the message */
  id: string;
  /** Role: 'user' or 'assistant' */
  role: 'user' | 'assistant';
  /** Message content */
  content: string;
  /** ISO timestamp of creation */
  created_at: string;
}

/**
 * Conversation summary (for list view)
 */
export interface Conversation {
  /** UUID of the conversation */
  id: string;
  /** Title (first message preview or null) */
  title: string | null;
  /** ISO timestamp of creation */
  created_at: string;
  /** ISO timestamp of last update */
  updated_at: string;
}

/**
 * Response from GET /api/chat/conversations
 */
export interface ConversationListResponse {
  /** List of conversations */
  conversations: Conversation[];
  /** Total count */
  total: number;
}

/**
 * Response from GET /api/chat/conversations/{id}
 */
export interface ConversationDetailResponse {
  /** UUID of the conversation */
  id: string;
  /** Title (first message preview or null) */
  title: string | null;
  /** All messages in the conversation */
  messages: Message[];
  /** ISO timestamp of creation */
  created_at: string;
  /** ISO timestamp of last update */
  updated_at: string;
}

// ============================================================
// Error Types
// ============================================================

/**
 * API error response format
 */
export interface ApiErrorResponse {
  /** Error type/code */
  error?: string;
  /** Human-readable error message */
  detail: string;
}

// ============================================================
// Frontend State Types
// ============================================================

/**
 * Local message for optimistic UI (before server confirms)
 */
export interface LocalMessage extends Message {
  /** Pending status for optimistic updates */
  status?: 'pending' | 'sent' | 'error';
}

/**
 * Chat hook state
 */
export interface ChatState {
  /** Current messages in view */
  messages: LocalMessage[];
  /** Current conversation ID (null for new chat) */
  conversationId: string | null;
  /** Loading state for API calls */
  isLoading: boolean;
  /** Error message if any */
  error: string | null;
}

/**
 * Chat hook actions
 */
export interface ChatActions {
  /** Send a message */
  sendMessage: (message: string) => Promise<void>;
  /** Load an existing conversation */
  loadConversation: (id: string) => Promise<void>;
  /** Start a new conversation (clear state) */
  startNewChat: () => void;
  /** Retry failed message */
  retryMessage: (messageId: string) => Promise<void>;
  /** Clear error */
  clearError: () => void;
}
