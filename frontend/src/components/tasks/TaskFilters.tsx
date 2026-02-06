"use client";

import { useState } from "react";
import type { TaskFilterParams, TaskPriority, TagWithCount } from "@/lib/types";
import { PrioritySelect } from "@/components/ui/PrioritySelect";
import { DatePicker } from "@/components/ui/DatePicker";

interface TaskFiltersProps {
  filters: TaskFilterParams;
  onFilterChange: <K extends keyof TaskFilterParams>(key: K, value: TaskFilterParams[K]) => void;
  onReset: () => void;
  availableTags?: TagWithCount[];
  hasActiveFilters: boolean;
}

export function TaskFilters({
  filters,
  onFilterChange,
  onReset,
  availableTags = [],
  hasActiveFilters,
}: TaskFiltersProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="glass-card rounded-xl p-4">
      {/* Search bar and toggle */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <input
            type="text"
            value={filters.search || ""}
            onChange={(e) => onFilterChange("search", e.target.value || undefined)}
            placeholder="Search tasks..."
            className="input-field w-full pl-10"
          />
          <svg
            className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>

        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className={`
            btn-secondary flex items-center gap-2 px-4 py-2
            ${hasActiveFilters ? "border-[var(--accent-primary)] text-[var(--accent-primary)]" : ""}
          `}
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          Filters
          {hasActiveFilters && (
            <span className="w-2 h-2 rounded-full bg-[var(--accent-primary)]" />
          )}
        </button>

        {/* Sort controls */}
        <select
          value={filters.sort_by || "created_at"}
          onChange={(e) => onFilterChange("sort_by", e.target.value as TaskFilterParams["sort_by"])}
          className="input-field w-auto"
        >
          <option value="created_at">Created Date</option>
          <option value="due_date">Due Date</option>
          <option value="priority">Priority</option>
          <option value="title">Title</option>
        </select>

        <button
          onClick={() => onFilterChange("sort_order", filters.sort_order === "asc" ? "desc" : "asc")}
          className="btn-secondary p-2"
          title={filters.sort_order === "asc" ? "Sort ascending" : "Sort descending"}
        >
          {filters.sort_order === "asc" ? (
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
            </svg>
          ) : (
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4" />
            </svg>
          )}
        </button>
      </div>

      {/* Expanded filters */}
      {isExpanded && (
        <div className="mt-4 pt-4 border-t border-[var(--border-primary)] space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Priority filter */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-[var(--text-secondary)]">
                Priority
              </label>
              <select
                value={filters.priority || ""}
                onChange={(e) => onFilterChange("priority", e.target.value || undefined)}
                className="input-field w-full"
              >
                <option value="">All priorities</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
                <option value="high,urgent">High & Urgent</option>
              </select>
            </div>

            {/* Status filter */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-[var(--text-secondary)]">
                Status
              </label>
              <select
                value={filters.is_complete === undefined ? "" : String(filters.is_complete)}
                onChange={(e) => {
                  const value = e.target.value;
                  onFilterChange("is_complete", value === "" ? undefined : value === "true");
                }}
                className="input-field w-full"
              >
                <option value="">All tasks</option>
                <option value="false">Active</option>
                <option value="true">Completed</option>
              </select>
            </div>

            {/* Due date range */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-[var(--text-secondary)]">
                Due after
              </label>
              <DatePicker
                value={filters.due_after || ""}
                onChange={(value) => onFilterChange("due_after", value || undefined)}
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium text-[var(--text-secondary)]">
                Due before
              </label>
              <DatePicker
                value={filters.due_before || ""}
                onChange={(value) => onFilterChange("due_before", value || undefined)}
              />
            </div>
          </div>

          {/* Tags filter */}
          {availableTags.length > 0 && (
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-[var(--text-secondary)]">
                Tags
              </label>
              <div className="flex flex-wrap gap-2">
                {availableTags.map((tag) => {
                  const isSelected = filters.tags?.split(",").includes(tag.name);
                  return (
                    <button
                      key={tag.id}
                      type="button"
                      onClick={() => {
                        const currentTags = filters.tags?.split(",").filter(Boolean) || [];
                        const newTags = isSelected
                          ? currentTags.filter((t) => t !== tag.name)
                          : [...currentTags, tag.name];
                        onFilterChange("tags", newTags.length > 0 ? newTags.join(",") : undefined);
                      }}
                      className={`
                        px-3 py-1.5 rounded-full text-sm font-medium transition-all
                        ${isSelected
                          ? "bg-[var(--accent-primary)] text-white"
                          : "bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:bg-[var(--bg-secondary)]"
                        }
                      `}
                    >
                      {tag.color && (
                        <span
                          className="inline-block w-2 h-2 rounded-full mr-1.5"
                          style={{ backgroundColor: tag.color }}
                        />
                      )}
                      {tag.name}
                      <span className="ml-1 opacity-60">({tag.task_count})</span>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Reset button */}
          {hasActiveFilters && (
            <div className="flex justify-end">
              <button
                onClick={onReset}
                className="text-sm text-[var(--accent-primary)] hover:underline flex items-center gap-1"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Reset filters
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
