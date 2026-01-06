"use client";

import { useCallback, useEffect, useState } from "react";

import { api, ApiError } from "@/lib/api";
import type {
  Task,
  TaskCreateRequest,
  TaskListResponse,
  TaskPatchRequest,
  TaskUpdateRequest,
} from "@/lib/types";

export function useTasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  const fetchTasks = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.get<TaskListResponse>("/tasks", true);
      setTasks(response.tasks);
      setTotal(response.total);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Failed to fetch tasks");
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const createTask = useCallback(async (data: TaskCreateRequest) => {
    try {
      const task = await api.post<Task>("/tasks", data, true);
      setTasks((prev) => [task, ...prev]);
      setTotal((prev) => prev + 1);
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
        const updatedTask = await api.put<Task>(`/tasks/${taskId}`, data, true);
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
        const updatedTask = await api.patch<Task>(
          `/tasks/${taskId}`,
          data,
          true
        );
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
      await api.delete(`/tasks/${taskId}`, true);
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
      setTotal((prev) => prev - 1);
    } catch (err) {
      if (err instanceof ApiError) {
        throw new Error(err.message);
      }
      throw new Error("Failed to delete task");
    }
  }, []);

  const toggleTask = useCallback(async (taskId: string) => {
    try {
      const updatedTask = await api.patch<Task>(
        `/tasks/${taskId}/toggle`,
        undefined,
        true
      );
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

  return {
    tasks,
    isLoading,
    error,
    total,
    fetchTasks,
    createTask,
    updateTask,
    patchTask,
    deleteTask,
    toggleTask,
  };
}
