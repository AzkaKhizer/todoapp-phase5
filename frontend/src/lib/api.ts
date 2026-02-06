/**
 * API client with JWT authentication.
 */

import { getAuthToken } from "./auth-client";
import type {
  Task,
  TaskListResponse,
  TaskCreateRequest,
  TaskUpdateRequest,
  TaskPatchRequest,
  TaskFilterParams,
  TagWithCount,
  TagListResponse,
  TagCreateRequest,
  ActivityLogEntry,
  ActivityListResponse,
  ActivityFilterParams,
  ActivityTypeCount,
  ProductivitySummary,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = response.statusText;
    let errorCode = "UNKNOWN";

    try {
      const errorData = await response.json();
      if (typeof errorData.detail === "string") {
        errorMessage = errorData.detail;
      } else if (errorData.message) {
        errorMessage = errorData.message;
      }
      if (errorData.error) {
        errorCode = errorData.error;
      }
    } catch {
      // JSON parsing failed
    }

    throw new ApiError(response.status, errorCode, errorMessage);
  }

  // Handle 204 No Content responses (e.g., DELETE)
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

async function getAuthHeaders(): Promise<HeadersInit> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };

  const token = await getAuthToken();
  // T004: Debug logging for auth flow
  if (process.env.NODE_ENV === "development") {
    console.log("[API] Auth token:", token ? "Present" : "Missing");
  }
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  } else {
    console.warn("[API] No auth token available - request may fail with 401");
  }

  return headers;
}

function getBasicHeaders(): HeadersInit {
  return {
    "Content-Type": "application/json",
  };
}

export const api = {
  async get<T>(path: string, authenticated: boolean = false): Promise<T> {
    const headers = authenticated ? await getAuthHeaders() : getBasicHeaders();
    const response = await fetch(`${API_URL}${path}`, {
      method: "GET",
      headers,
    });
    return handleResponse<T>(response);
  },

  async post<T>(
    path: string,
    data?: unknown,
    authenticated: boolean = false
  ): Promise<T> {
    const headers = authenticated ? await getAuthHeaders() : getBasicHeaders();
    const response = await fetch(`${API_URL}${path}`, {
      method: "POST",
      headers,
      body: data ? JSON.stringify(data) : undefined,
    });
    return handleResponse<T>(response);
  },

  async put<T>(
    path: string,
    data: unknown,
    authenticated: boolean = true
  ): Promise<T> {
    const headers = authenticated ? await getAuthHeaders() : getBasicHeaders();
    const response = await fetch(`${API_URL}${path}`, {
      method: "PUT",
      headers,
      body: JSON.stringify(data),
    });
    return handleResponse<T>(response);
  },

  async patch<T>(
    path: string,
    data?: unknown,
    authenticated: boolean = true
  ): Promise<T> {
    const headers = authenticated ? await getAuthHeaders() : getBasicHeaders();
    const response = await fetch(`${API_URL}${path}`, {
      method: "PATCH",
      headers,
      body: data ? JSON.stringify(data) : undefined,
    });
    return handleResponse<T>(response);
  },

  async delete(path: string, authenticated: boolean = true): Promise<void> {
    const headers = authenticated ? await getAuthHeaders() : getBasicHeaders();
    const response = await fetch(`${API_URL}${path}`, {
      method: "DELETE",
      headers,
    });
    await handleResponse<void>(response);
  },
};

// ============================================================
// Task API Functions
// ============================================================

function buildQueryString(params: TaskFilterParams): string {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.set(key, String(value));
    }
  });

  const queryString = searchParams.toString();
  return queryString ? `?${queryString}` : "";
}

export const taskApi = {
  async list(filters: TaskFilterParams = {}): Promise<TaskListResponse> {
    const queryString = buildQueryString(filters);
    return api.get<TaskListResponse>(`/tasks${queryString}`, true);
  },

  async get(taskId: string): Promise<Task> {
    return api.get<Task>(`/tasks/${taskId}`, true);
  },

  async create(data: TaskCreateRequest): Promise<Task> {
    // Convert due_date to ISO string if present
    const payload = {
      ...data,
      due_date: data.due_date ? new Date(data.due_date).toISOString() : undefined,
    };
    return api.post<Task>("/tasks", payload, true);
  },

  async update(taskId: string, data: TaskUpdateRequest): Promise<Task> {
    const payload = {
      ...data,
      due_date: data.due_date ? new Date(data.due_date).toISOString() : null,
    };
    return api.put<Task>(`/tasks/${taskId}`, payload, true);
  },

  async patch(taskId: string, data: TaskPatchRequest): Promise<Task> {
    const payload = { ...data };
    if (data.due_date) {
      payload.due_date = new Date(data.due_date).toISOString();
    }
    return api.patch<Task>(`/tasks/${taskId}`, payload, true);
  },

  async delete(taskId: string): Promise<void> {
    return api.delete(`/tasks/${taskId}`, true);
  },

  async toggle(taskId: string): Promise<Task> {
    return api.patch<Task>(`/tasks/${taskId}/toggle`, undefined, true);
  },
};

// ============================================================
// Tag API Functions
// ============================================================

export const tagApi = {
  async list(): Promise<TagWithCount[]> {
    const response = await api.get<TagListResponse>("/tags", true);
    return response.data;
  },

  async create(data: TagCreateRequest): Promise<TagWithCount> {
    return api.post<TagWithCount>("/tags", data, true);
  },

  async delete(tagId: string): Promise<void> {
    return api.delete(`/tags/${tagId}`, true);
  },
};

// ============================================================
// Activity Log API Functions
// ============================================================

function buildActivityQueryString(params: ActivityFilterParams): string {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.set(key, String(value));
    }
  });

  const queryString = searchParams.toString();
  return queryString ? `?${queryString}` : "";
}

export const activityApi = {
  async list(filters: ActivityFilterParams = {}): Promise<ActivityListResponse> {
    const queryString = buildActivityQueryString(filters);
    return api.get<ActivityListResponse>(`/activities${queryString}`, true);
  },

  async get(activityId: string): Promise<ActivityLogEntry> {
    return api.get<ActivityLogEntry>(`/activities/${activityId}`, true);
  },

  async getEntityHistory(
    entityType: string,
    entityId: string,
    limit: number = 100
  ): Promise<ActivityLogEntry[]> {
    return api.get<ActivityLogEntry[]>(
      `/activities/entity/${entityType}/${entityId}?limit=${limit}`,
      true
    );
  },

  async getProductivity(days: number = 7): Promise<ProductivitySummary> {
    return api.get<ProductivitySummary>(`/activities/productivity?days=${days}`, true);
  },

  async getActivityTypes(limit: number = 10): Promise<ActivityTypeCount[]> {
    return api.get<ActivityTypeCount[]>(`/activities/types?limit=${limit}`, true);
  },
};
