/**
 * API type definitions for the Todo application.
 */

export interface User {
  id: string;
  email: string;
  created_at: string;
}

export type TaskPriority = "low" | "medium" | "high" | "urgent";

export interface Tag {
  id: string;
  name: string;
  color: string | null;
}

export interface TagWithCount extends Tag {
  task_count: number;
}

export interface ReminderInfo {
  id: string;
  scheduled_time: string;
  status: string;
}

export interface RecurrenceInfo {
  id: string;
  type: string;
  interval: number;
  days_of_week: number[] | null;
  day_of_month: number | null;
  end_date: string | null;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  is_complete: boolean;
  user_id: string;
  due_date: string | null;
  priority: TaskPriority;
  tags: Tag[];
  reminder: ReminderInfo | null;
  recurrence: RecurrenceInfo | null;
  is_overdue: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

export interface PaginationInfo {
  page: number;
  limit: number;
  total_items: number;
  total_pages: number;
}

export interface TaskListResponse {
  data: Task[];
  pagination: PaginationInfo;
}

export interface TagListResponse {
  data: TagWithCount[];
}

export interface ErrorResponse {
  error: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface MessageResponse {
  message: string;
}

// Request types
export interface UserCreateRequest {
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RecurrenceCreateRequest {
  type: "daily" | "weekly" | "monthly" | "yearly" | "custom";
  interval?: number;
  days_of_week?: number[];
  day_of_month?: number;
  end_date?: string;
}

export interface TaskCreateRequest {
  title: string;
  description?: string;
  due_date?: string;
  priority?: TaskPriority;
  tags?: string[];
  reminder_offset_minutes?: number;
  recurrence?: RecurrenceCreateRequest;
}

export interface TaskUpdateRequest {
  title: string;
  description: string;
  due_date?: string | null;
  priority?: TaskPriority;
  tags?: string[];
  reminder_offset_minutes?: number | null;
  recurrence?: RecurrenceCreateRequest | null;
}

export interface TaskPatchRequest {
  title?: string;
  description?: string;
  is_complete?: boolean;
  due_date?: string | null;
  priority?: TaskPriority;
  tags?: string[];
  reminder_offset_minutes?: number;
}

export interface TaskFilterParams {
  page?: number;
  limit?: number;
  search?: string;
  priority?: string;
  due_before?: string;
  due_after?: string;
  tags?: string;
  is_complete?: boolean;
  sort_by?: "due_date" | "priority" | "created_at" | "title";
  sort_order?: "asc" | "desc";
}

export interface TagCreateRequest {
  name: string;
  color?: string;
}

// ============================================================
// Chat Types
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
export interface ChatMessage {
  /** UUID of the message */
  id: string;
  /** Role: 'user' or 'assistant' */
  role: "user" | "assistant";
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
  messages: ChatMessage[];
  /** ISO timestamp of creation */
  created_at: string;
  /** ISO timestamp of last update */
  updated_at: string;
}

/**
 * Local message for optimistic UI (before server confirms)
 */
export interface LocalChatMessage extends ChatMessage {
  /** Pending status for optimistic updates */
  status?: "pending" | "sent" | "error";
}

// ============================================================
// Notification Types
// ============================================================

/**
 * Notification type for in-app notifications
 */
export type NotificationType = "reminder" | "success" | "error" | "info";

/**
 * In-app notification structure
 */
export interface Notification {
  /** Unique notification ID */
  id: string;
  /** Type of notification */
  type: NotificationType;
  /** Notification title */
  title: string;
  /** Notification body/message */
  body: string;
  /** Optional action URL to navigate to */
  action_url?: string;
  /** ISO timestamp when notification was received */
  timestamp: string;
}

/**
 * Reminder-specific notification data from the server
 */
export interface ReminderNotification {
  reminder_id: string;
  task_id: string;
  user_id: string;
  task_title: string;
  task_due_date: string;
  delivery_channel: string;
}

// ============================================================
// Activity Log Types
// ============================================================

/**
 * Activity log entry from the server
 */
export interface ActivityLogEntry {
  /** Unique activity ID */
  id: string;
  /** User who performed the action */
  user_id: string;
  /** Type of event (e.g., task.created, task.completed) */
  event_type: string;
  /** Type of entity (task, reminder, tag) */
  entity_type: string;
  /** ID of the affected entity */
  entity_id: string;
  /** ISO timestamp when the event occurred */
  timestamp: string;
  /** Additional event details */
  details: Record<string, unknown>;
  /** Request correlation ID for tracing */
  correlation_id?: string | null;
}

/**
 * Response from GET /api/activities
 */
export interface ActivityListResponse {
  data: ActivityLogEntry[];
  pagination: PaginationInfo;
}

/**
 * Activity filter parameters
 */
export interface ActivityFilterParams {
  entity_type?: string;
  entity_id?: string;
  event_type?: string;
  start_date?: string;
  end_date?: string;
  page?: number;
  limit?: number;
}

/**
 * Activity type with count
 */
export interface ActivityTypeCount {
  event_type: string;
  count: number;
}

/**
 * Daily completion data for productivity chart
 */
export interface DailyCompletion {
  date: string;
  count: number;
}

/**
 * Productivity summary response
 */
export interface ProductivitySummary {
  period_days: number;
  start_date: string;
  end_date: string;
  tasks_completed: number;
  tasks_created: number;
  tasks_deleted: number;
  net_tasks: number;
  completion_rate: number;
  completions_by_day: DailyCompletion[];
}
