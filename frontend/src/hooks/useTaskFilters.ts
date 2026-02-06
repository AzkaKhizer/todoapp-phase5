"use client";

import { useState, useCallback, useMemo } from "react";
import type { TaskFilterParams, TaskPriority } from "@/lib/types";

interface UseTaskFiltersOptions {
  defaultFilters?: Partial<TaskFilterParams>;
}

interface UseTaskFiltersReturn {
  filters: TaskFilterParams;
  setFilter: <K extends keyof TaskFilterParams>(key: K, value: TaskFilterParams[K]) => void;
  setFilters: (filters: Partial<TaskFilterParams>) => void;
  resetFilters: () => void;
  hasActiveFilters: boolean;
  activeFilterCount: number;
  queryString: string;
}

const DEFAULT_FILTERS: TaskFilterParams = {
  page: 1,
  limit: 20,
  sort_by: "created_at",
  sort_order: "desc",
};

export function useTaskFilters(options: UseTaskFiltersOptions = {}): UseTaskFiltersReturn {
  const initialFilters = useMemo(
    () => ({ ...DEFAULT_FILTERS, ...options.defaultFilters }),
    [options.defaultFilters]
  );

  const [filters, setFiltersState] = useState<TaskFilterParams>(initialFilters);

  const setFilter = useCallback(<K extends keyof TaskFilterParams>(
    key: K,
    value: TaskFilterParams[K]
  ) => {
    setFiltersState((prev) => {
      // Reset page when filters change (except when changing page itself)
      const newFilters = { ...prev, [key]: value };
      if (key !== "page") {
        newFilters.page = 1;
      }
      return newFilters;
    });
  }, []);

  const setFilters = useCallback((newFilters: Partial<TaskFilterParams>) => {
    setFiltersState((prev) => ({ ...prev, ...newFilters, page: 1 }));
  }, []);

  const resetFilters = useCallback(() => {
    setFiltersState(initialFilters);
  }, [initialFilters]);

  const hasActiveFilters = useMemo(() => {
    return !!(
      filters.search ||
      filters.priority ||
      filters.due_before ||
      filters.due_after ||
      filters.tags ||
      filters.is_complete !== undefined
    );
  }, [filters]);

  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (filters.search) count++;
    if (filters.priority) count++;
    if (filters.due_before || filters.due_after) count++;
    if (filters.tags) count++;
    if (filters.is_complete !== undefined) count++;
    return count;
  }, [filters]);

  const queryString = useMemo(() => {
    const params = new URLSearchParams();

    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        params.set(key, String(value));
      }
    });

    return params.toString();
  }, [filters]);

  return {
    filters,
    setFilter,
    setFilters,
    resetFilters,
    hasActiveFilters,
    activeFilterCount,
    queryString,
  };
}

// Priority filter helpers
export function parsePriorityFilter(value: string | undefined): TaskPriority[] {
  if (!value) return [];
  return value.split(",") as TaskPriority[];
}

export function formatPriorityFilter(priorities: TaskPriority[]): string {
  return priorities.join(",");
}

// Tag filter helpers
export function parseTagFilter(value: string | undefined): string[] {
  if (!value) return [];
  return value.split(",");
}

export function formatTagFilter(tags: string[]): string {
  return tags.join(",");
}
