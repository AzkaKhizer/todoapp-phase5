"use client";

import { useState, useMemo } from "react";
import { useActivities, useProductivity } from "@/hooks/useActivities";
import type { ActivityLogEntry } from "@/lib/types";

interface ActivityLogProps {
  showProductivity?: boolean;
  limit?: number;
  entityType?: string;
  entityId?: string;
}

const EVENT_TYPE_ICONS: Record<string, string> = {
  "task.created": "+",
  "task.updated": "~",
  "task.completed": "v",
  "task.deleted": "x",
  "reminder.created": "!",
  "reminder.sent": ">",
  "tag.created": "#",
  "tag.deleted": "-",
};

const EVENT_TYPE_COLORS: Record<string, string> = {
  "task.created": "text-green-600 bg-green-100",
  "task.updated": "text-blue-600 bg-blue-100",
  "task.completed": "text-purple-600 bg-purple-100",
  "task.deleted": "text-red-600 bg-red-100",
  "reminder.created": "text-yellow-600 bg-yellow-100",
  "reminder.sent": "text-orange-600 bg-orange-100",
  "tag.created": "text-teal-600 bg-teal-100",
  "tag.deleted": "text-gray-600 bg-gray-100",
};

function formatEventType(eventType: string): string {
  return eventType
    .split(".")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;

  return date.toLocaleDateString();
}

function ActivityItem({ activity }: { activity: ActivityLogEntry }) {
  const icon = EVENT_TYPE_ICONS[activity.event_type] || "?";
  const colorClass = EVENT_TYPE_COLORS[activity.event_type] || "text-gray-600 bg-gray-100";
  const detailTitle =
    activity.details && "title" in activity.details
      ? String(activity.details.title)
      : null;

  return (
    <div className="flex items-start gap-3 py-3 border-b border-gray-100 last:border-0">
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${colorClass}`}
      >
        {icon}
      </div>
      <div className="flex-grow min-w-0">
        <div className="flex items-center justify-between gap-2">
          <span className="font-medium text-gray-900 truncate">
            {formatEventType(activity.event_type)}
          </span>
          <span className="text-xs text-gray-500 flex-shrink-0">
            {formatTimestamp(activity.timestamp)}
          </span>
        </div>
        <div className="text-sm text-gray-600 mt-0.5">
          {activity.entity_type}: {activity.entity_id.slice(0, 8)}...
        </div>
        {detailTitle && (
          <div className="text-xs text-gray-500 mt-1">
            <span className="inline-block">{detailTitle}</span>
          </div>
        )}
      </div>
    </div>
  );
}

function ProductivityChart({
  completionsByDay,
}: {
  completionsByDay: Array<{ date: string; count: number }>;
}) {
  const maxCount = Math.max(...completionsByDay.map((d) => d.count), 1);

  return (
    <div className="flex items-end gap-1 h-20">
      {completionsByDay.map((day) => (
        <div
          key={day.date}
          className="flex-1 flex flex-col items-center gap-1"
          title={`${day.date}: ${day.count} tasks`}
        >
          <div
            className="w-full bg-purple-500 rounded-t transition-all duration-300"
            style={{
              height: `${Math.max((day.count / maxCount) * 100, 4)}%`,
              minHeight: day.count > 0 ? "8px" : "2px",
            }}
          />
          <span className="text-xs text-gray-500">
            {new Date(day.date).toLocaleDateString("en", { weekday: "narrow" })}
          </span>
        </div>
      ))}
    </div>
  );
}

function ProductivitySummaryCard() {
  const [days, setDays] = useState(7);
  const { summary, isLoading, error, refresh } = useProductivity(days);

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4" />
        <div className="h-20 bg-gray-200 rounded" />
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-red-600 text-sm">{error || "Failed to load productivity data"}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900">Productivity</h3>
        <select
          value={days}
          onChange={(e) => {
            setDays(Number(e.target.value));
            refresh(Number(e.target.value));
          }}
          className="text-sm border rounded px-2 py-1"
        >
          <option value={7}>Last 7 days</option>
          <option value={14}>Last 14 days</option>
          <option value={30}>Last 30 days</option>
        </select>
      </div>

      <ProductivityChart completionsByDay={summary.completions_by_day} />

      <div className="grid grid-cols-3 gap-4 mt-6">
        <div className="text-center">
          <div className="text-2xl font-bold text-purple-600">{summary.tasks_completed}</div>
          <div className="text-xs text-gray-500">Completed</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">{summary.tasks_created}</div>
          <div className="text-xs text-gray-500">Created</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">{summary.completion_rate}%</div>
          <div className="text-xs text-gray-500">Rate</div>
        </div>
      </div>
    </div>
  );
}

export function ActivityLog({
  showProductivity = true,
  limit = 20,
  entityType,
  entityId,
}: ActivityLogProps) {
  const [eventTypeFilter, setEventTypeFilter] = useState<string>("");

  const { activities, isLoading, error, pagination, fetchActivities, updateFilters } =
    useActivities({
      initialFilters: {
        limit,
        entity_type: entityType,
        entity_id: entityId,
      },
    });

  const filteredActivities = useMemo(() => {
    if (!eventTypeFilter) return activities;
    return activities.filter((a) => a.event_type === eventTypeFilter);
  }, [activities, eventTypeFilter]);

  const uniqueEventTypes = useMemo(() => {
    const types = new Set(activities.map((a) => a.event_type));
    return Array.from(types).sort();
  }, [activities]);

  const handleFilterChange = (eventType: string) => {
    setEventTypeFilter(eventType);
    updateFilters({
      limit,
      entity_type: entityType,
      entity_id: entityId,
      event_type: eventType || undefined,
    });
  };

  if (isLoading && activities.length === 0) {
    return (
      <div className="space-y-6">
        {showProductivity && (
          <div className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="h-6 bg-gray-200 rounded w-1/3 mb-4" />
            <div className="h-20 bg-gray-200 rounded" />
          </div>
        )}
        <div className="bg-white rounded-lg shadow p-6 animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/4 mb-4" />
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="flex gap-3">
                <div className="w-8 h-8 bg-gray-200 rounded-full" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-1/2" />
                  <div className="h-3 bg-gray-200 rounded w-1/3" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {showProductivity && <ProductivitySummaryCard />}

      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-gray-900">Activity Log</h3>
            <select
              value={eventTypeFilter}
              onChange={(e) => handleFilterChange(e.target.value)}
              className="text-sm border rounded px-2 py-1"
            >
              <option value="">All activities</option>
              {uniqueEventTypes.map((type) => (
                <option key={type} value={type}>
                  {formatEventType(type)}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="p-4">
          {error ? (
            <p className="text-red-600 text-sm">{error}</p>
          ) : filteredActivities.length === 0 ? (
            <p className="text-gray-500 text-sm text-center py-8">No activities found</p>
          ) : (
            <div className="divide-y divide-gray-100">
              {filteredActivities.map((activity) => (
                <ActivityItem key={activity.id} activity={activity} />
              ))}
            </div>
          )}

          {pagination.page < pagination.total_pages && (
            <button
              onClick={() => fetchActivities({ page: pagination.page + 1 })}
              disabled={isLoading}
              className="w-full mt-4 py-2 text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50"
            >
              {isLoading ? "Loading..." : "Load more"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default ActivityLog;
