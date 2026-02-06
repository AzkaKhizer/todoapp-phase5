"use client";

import { useCallback, useEffect, useState } from "react";

import { useSession } from "@/lib/auth-client";
import { activityApi, ApiError } from "@/lib/api";
import type {
  ActivityLogEntry,
  ActivityFilterParams,
  ActivityTypeCount,
  ProductivitySummary,
  PaginationInfo,
} from "@/lib/types";

interface UseActivitiesOptions {
  initialFilters?: ActivityFilterParams;
  autoLoad?: boolean;
}

export function useActivities(options: UseActivitiesOptions = {}) {
  const { initialFilters = {}, autoLoad = true } = options;
  const { data: session, isPending: isSessionLoading } = useSession();
  const [activities, setActivities] = useState<ActivityLogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState<PaginationInfo>({
    page: 1,
    limit: 20,
    total_items: 0,
    total_pages: 0,
  });
  const [filters, setFilters] = useState<ActivityFilterParams>(initialFilters);

  const fetchActivities = useCallback(
    async (filterOverrides?: ActivityFilterParams) => {
      if (!session?.user) {
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const appliedFilters = { ...filters, ...filterOverrides };
        const response = await activityApi.list(appliedFilters);
        setActivities(response.data);
        setPagination(response.pagination);
      } catch (err) {
        console.error("Activity fetch error:", err);
        if (err instanceof ApiError) {
          setError(err.message);
        } else {
          setError("Failed to fetch activities");
        }
      } finally {
        setIsLoading(false);
      }
    },
    [session?.user, filters]
  );

  useEffect(() => {
    if (!isSessionLoading && session?.user && autoLoad) {
      fetchActivities();
    } else if (!isSessionLoading && !session?.user) {
      setIsLoading(false);
    }
  }, [isSessionLoading, session?.user, autoLoad, fetchActivities]);

  const updateFilters = useCallback((newFilters: ActivityFilterParams) => {
    setFilters(newFilters);
  }, []);

  const loadMore = useCallback(async () => {
    if (pagination.page < pagination.total_pages) {
      await fetchActivities({ ...filters, page: pagination.page + 1 });
    }
  }, [fetchActivities, filters, pagination]);

  return {
    activities,
    isLoading,
    error,
    pagination,
    filters,
    fetchActivities,
    updateFilters,
    loadMore,
  };
}

export function useProductivity(days: number = 7) {
  const { data: session, isPending: isSessionLoading } = useSession();
  const [summary, setSummary] = useState<ProductivitySummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProductivity = useCallback(
    async (periodDays?: number) => {
      if (!session?.user) {
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const data = await activityApi.getProductivity(periodDays ?? days);
        setSummary(data);
      } catch (err) {
        console.error("Productivity fetch error:", err);
        if (err instanceof ApiError) {
          setError(err.message);
        } else {
          setError("Failed to fetch productivity data");
        }
      } finally {
        setIsLoading(false);
      }
    },
    [session?.user, days]
  );

  useEffect(() => {
    if (!isSessionLoading && session?.user) {
      fetchProductivity();
    } else if (!isSessionLoading && !session?.user) {
      setIsLoading(false);
    }
  }, [isSessionLoading, session?.user, fetchProductivity]);

  return {
    summary,
    isLoading,
    error,
    refresh: fetchProductivity,
  };
}

export function useActivityTypes() {
  const { data: session, isPending: isSessionLoading } = useSession();
  const [types, setTypes] = useState<ActivityTypeCount[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTypes = useCallback(async () => {
    if (!session?.user) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await activityApi.getActivityTypes();
      setTypes(data);
    } catch (err) {
      console.error("Activity types fetch error:", err);
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Failed to fetch activity types");
      }
    } finally {
      setIsLoading(false);
    }
  }, [session?.user]);

  useEffect(() => {
    if (!isSessionLoading && session?.user) {
      fetchTypes();
    } else if (!isSessionLoading && !session?.user) {
      setIsLoading(false);
    }
  }, [isSessionLoading, session?.user, fetchTypes]);

  return {
    types,
    isLoading,
    error,
    refresh: fetchTypes,
  };
}

export function useEntityHistory(entityType: string, entityId: string) {
  const { data: session, isPending: isSessionLoading } = useSession();
  const [history, setHistory] = useState<ActivityLogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHistory = useCallback(async () => {
    if (!session?.user || !entityType || !entityId) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await activityApi.getEntityHistory(entityType, entityId);
      setHistory(data);
    } catch (err) {
      console.error("Entity history fetch error:", err);
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Failed to fetch entity history");
      }
    } finally {
      setIsLoading(false);
    }
  }, [session?.user, entityType, entityId]);

  useEffect(() => {
    if (!isSessionLoading && session?.user && entityType && entityId) {
      fetchHistory();
    } else if (!isSessionLoading) {
      setIsLoading(false);
    }
  }, [isSessionLoading, session?.user, entityType, entityId, fetchHistory]);

  return {
    history,
    isLoading,
    error,
    refresh: fetchHistory,
  };
}
