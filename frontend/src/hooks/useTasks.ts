"use client";

import { useCallback, useEffect, useState } from "react";

import { useSession } from "@/lib/auth-client";
import { taskApi, ApiError } from "@/lib/api";
import { useTaskSync } from "./useWebSocket";
import type {
  Task,
  TaskCreateRequest,
  TaskPatchRequest,
  TaskUpdateRequest,
  TaskFilterParams,
  PaginationInfo,
} from "@/lib/types";

interface UseTasksOptions {
  /** Initial filter parameters */
  initialFilters?: TaskFilterParams;
  /** Enable real-time sync via WebSocket */
  enableRealtimeSync?: boolean;
}

export function useTasks(options: UseTasksOptions | TaskFilterParams = {}) {
  // Handle both old and new API signatures
  const { initialFilters, enableRealtimeSync = true } =
    "initialFilters" in options || "enableRealtimeSync" in options
      ? (options as UseTasksOptions)
      : { initialFilters: options as TaskFilterParams, enableRealtimeSync: true };
  const { data: session, isPending: isSessionLoading } = useSession();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState<PaginationInfo>({
    page: 1,
    limit: 20,
    total_items: 0,
    total_pages: 0,
  });
  const [filters, setFilters] = useState<TaskFilterParams>(initialFilters || {});

  const fetchTasks = useCallback(async (filterOverrides?: TaskFilterParams) => {
    if (!session?.user) {
      console.log("No session, skipping task fetch");
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const appliedFilters = { ...filters, ...filterOverrides };
      console.log("Fetching tasks for user:", session.user.id, "with filters:", appliedFilters);
      const response = await taskApi.list(appliedFilters);
      setTasks(response.data);
      setPagination(response.pagination);
    } catch (err) {
      console.error("Task fetch error:", err);
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Failed to fetch tasks");
      }
    } finally {
      setIsLoading(false);
    }
  }, [session?.user, filters]);

  useEffect(() => {
    // Only fetch when session is loaded and user is authenticated
    if (!isSessionLoading && session?.user) {
      fetchTasks();
    } else if (!isSessionLoading && !session?.user) {
      setIsLoading(false);
    }
  }, [isSessionLoading, session?.user, fetchTasks]);

  const createTask = useCallback(async (data: TaskCreateRequest) => {
    try {
      const task = await taskApi.create(data);
      setTasks((prev) => [task, ...prev]);
      setPagination((prev) => ({ ...prev, total_items: prev.total_items + 1 }));
      return task;
    } catch (err) {
      if (err instanceof ApiError) {
        throw new Error(err.message);
      }
      throw new Error("Failed to create task");
    }
  }, []);

  const updateTask = useCallback(
    async (taskId: string, data: TaskUpdateRequest) => {
      try {
        const updatedTask = await taskApi.update(taskId, data);
        setTasks((prev) =>
          prev.map((t) => (t.id === taskId ? updatedTask : t))
        );
        return updatedTask;
      } catch (err) {
        if (err instanceof ApiError) {
          throw new Error(err.message);
        }
        throw new Error("Failed to update task");
      }
    },
    []
  );

  const patchTask = useCallback(
    async (taskId: string, data: TaskPatchRequest) => {
      try {
        const updatedTask = await taskApi.patch(taskId, data);
        setTasks((prev) =>
          prev.map((t) => (t.id === taskId ? updatedTask : t))
        );
        return updatedTask;
      } catch (err) {
        if (err instanceof ApiError) {
          throw new Error(err.message);
        }
        throw new Error("Failed to update task");
      }
    },
    []
  );

  const deleteTask = useCallback(async (taskId: string) => {
    try {
      await taskApi.delete(taskId);
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
      setPagination((prev) => ({ ...prev, total_items: prev.total_items - 1 }));
    } catch (err) {
      if (err instanceof ApiError) {
        throw new Error(err.message);
      }
      throw new Error("Failed to delete task");
    }
  }, []);

  const toggleTask = useCallback(async (taskId: string) => {
    try {
      const updatedTask = await taskApi.toggle(taskId);
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? updatedTask : t))
      );
      return updatedTask;
    } catch (err) {
      if (err instanceof ApiError) {
        throw new Error(err.message);
      }
      throw new Error("Failed to toggle task");
    }
  }, []);

  const updateFilters = useCallback((newFilters: TaskFilterParams) => {
    setFilters(newFilters);
  }, []);

  // Real-time sync via WebSocket
  const handleTaskCreated = useCallback(
    (taskData: Record<string, unknown>) => {
      // Only add if we don't already have this task
      const newTask = taskData as unknown as Task;
      setTasks((prev) => {
        if (prev.some((t) => t.id === newTask.id)) {
          return prev;
        }
        return [newTask, ...prev];
      });
      setPagination((prev) => ({ ...prev, total_items: prev.total_items + 1 }));
    },
    []
  );

  const handleTaskUpdated = useCallback(
    (taskData: Record<string, unknown>) => {
      const updatedTask = taskData as unknown as Task;
      setTasks((prev) =>
        prev.map((t) => (t.id === updatedTask.id ? updatedTask : t))
      );
    },
    []
  );

  const handleTaskDeleted = useCallback((taskId: string) => {
    setTasks((prev) => prev.filter((t) => t.id !== taskId));
    setPagination((prev) => ({
      ...prev,
      total_items: Math.max(0, prev.total_items - 1),
    }));
  }, []);

  // Connect to WebSocket for real-time sync
  const { connectionState, isConnected } = useTaskSync(
    enableRealtimeSync
      ? {
          onTaskCreated: handleTaskCreated,
          onTaskUpdated: handleTaskUpdated,
          onTaskDeleted: handleTaskDeleted,
        }
      : {}
  );

  return {
    tasks,
    isLoading,
    error,
    pagination,
    total: pagination.total_items,
    filters,
    fetchTasks,
    createTask,
    updateTask,
    patchTask,
    deleteTask,
    toggleTask,
    updateFilters,
    // Real-time sync status
    realtimeSync: {
      enabled: enableRealtimeSync,
      connectionState,
      isConnected,
    },
  };
}
