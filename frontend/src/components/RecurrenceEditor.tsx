"use client";

import { useState, useEffect } from "react";
import type { RecurrenceInfo } from "@/lib/types";

type RecurrenceType = "daily" | "weekly" | "monthly" | "yearly" | "custom";

interface RecurrenceEditorProps {
  value: RecurrenceInfo | null;
  onChange: (value: RecurrenceInfo | null) => void;
}

const WEEKDAYS = [
  { value: 0, label: "Mon" },
  { value: 1, label: "Tue" },
  { value: 2, label: "Wed" },
  { value: 3, label: "Thu" },
  { value: 4, label: "Fri" },
  { value: 5, label: "Sat" },
  { value: 6, label: "Sun" },
];

export function RecurrenceEditor({ value, onChange }: RecurrenceEditorProps) {
  const [enabled, setEnabled] = useState(!!value);
  const [type, setType] = useState<RecurrenceType>(
    (value?.type as RecurrenceType) || "daily"
  );
  const [interval, setInterval] = useState(value?.interval || 1);
  const [daysOfWeek, setDaysOfWeek] = useState<number[]>(
    value?.days_of_week || [0]
  );
  const [dayOfMonth, setDayOfMonth] = useState(value?.day_of_month || 1);
  const [endDate, setEndDate] = useState(value?.end_date || "");

  // Update parent when values change
  useEffect(() => {
    if (!enabled) {
      onChange(null);
      return;
    }

    const recurrence: RecurrenceInfo = {
      id: value?.id || "",
      type,
      interval,
      days_of_week: type === "weekly" ? daysOfWeek : null,
      day_of_month: type === "monthly" || type === "yearly" ? dayOfMonth : null,
      end_date: endDate || null,
    };

    onChange(recurrence);
  }, [enabled, type, interval, daysOfWeek, dayOfMonth, endDate, value?.id, onChange]);

  const toggleDayOfWeek = (day: number) => {
    setDaysOfWeek((prev) => {
      if (prev.includes(day)) {
        // Don't allow removing all days
        if (prev.length === 1) return prev;
        return prev.filter((d) => d !== day);
      }
      return [...prev, day].sort();
    });
  };

  const getIntervalLabel = () => {
    switch (type) {
      case "daily":
        return interval === 1 ? "day" : "days";
      case "weekly":
        return interval === 1 ? "week" : "weeks";
      case "monthly":
        return interval === 1 ? "month" : "months";
      case "yearly":
        return interval === 1 ? "year" : "years";
      case "custom":
        return interval === 1 ? "day" : "days";
      default:
        return "units";
    }
  };

  return (
    <div className="space-y-4">
      {/* Enable/Disable toggle */}
      <label className="flex items-center gap-3 cursor-pointer">
        <div className="relative">
          <input
            type="checkbox"
            checked={enabled}
            onChange={(e) => setEnabled(e.target.checked)}
            className="sr-only"
          />
          <div
            className={`
              w-10 h-6 rounded-full transition-colors duration-200
              ${enabled ? "bg-[var(--accent-primary)]" : "bg-[var(--bg-tertiary)]"}
            `}
          >
            <div
              className={`
                absolute top-1 left-1 w-4 h-4 rounded-full bg-white transition-transform duration-200
                ${enabled ? "translate-x-4" : "translate-x-0"}
              `}
            />
          </div>
        </div>
        <span className="text-sm font-medium text-[var(--text-primary)]">
          Repeat this task
        </span>
      </label>

      {enabled && (
        <div className="space-y-4 pl-4 border-l-2 border-[var(--border-primary)]">
          {/* Recurrence type */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-[var(--text-secondary)]">
              Repeat
            </label>
            <div className="flex flex-wrap gap-2">
              {(["daily", "weekly", "monthly", "yearly"] as RecurrenceType[]).map(
                (t) => (
                  <button
                    key={t}
                    type="button"
                    onClick={() => setType(t)}
                    className={`
                      px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200
                      ${
                        type === t
                          ? "bg-[var(--accent-primary)] text-white"
                          : "bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:bg-[var(--bg-hover)]"
                      }
                    `}
                  >
                    {t.charAt(0).toUpperCase() + t.slice(1)}
                  </button>
                )
              )}
            </div>
          </div>

          {/* Interval */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-[var(--text-secondary)]">
              Every
            </label>
            <div className="flex items-center gap-2">
              <input
                type="number"
                min={1}
                max={365}
                value={interval}
                onChange={(e) => setInterval(Math.max(1, parseInt(e.target.value) || 1))}
                className="input-field w-20 text-center"
              />
              <span className="text-sm text-[var(--text-secondary)]">
                {getIntervalLabel()}
              </span>
            </div>
          </div>

          {/* Weekly: Day selection */}
          {type === "weekly" && (
            <div className="space-y-2">
              <label className="block text-sm font-medium text-[var(--text-secondary)]">
                On
              </label>
              <div className="flex flex-wrap gap-1">
                {WEEKDAYS.map(({ value, label }) => (
                  <button
                    key={value}
                    type="button"
                    onClick={() => toggleDayOfWeek(value)}
                    className={`
                      w-10 h-10 rounded-lg text-sm font-medium transition-all duration-200
                      ${
                        daysOfWeek.includes(value)
                          ? "bg-[var(--accent-primary)] text-white"
                          : "bg-[var(--bg-tertiary)] text-[var(--text-secondary)] hover:bg-[var(--bg-hover)]"
                      }
                    `}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Monthly: Day of month */}
          {type === "monthly" && (
            <div className="space-y-2">
              <label className="block text-sm font-medium text-[var(--text-secondary)]">
                On day
              </label>
              <select
                value={dayOfMonth}
                onChange={(e) => setDayOfMonth(parseInt(e.target.value))}
                className="input-field w-24"
              >
                {Array.from({ length: 31 }, (_, i) => i + 1).map((day) => (
                  <option key={day} value={day}>
                    {day}
                    {day === 1 || day === 21 || day === 31
                      ? "st"
                      : day === 2 || day === 22
                      ? "nd"
                      : day === 3 || day === 23
                      ? "rd"
                      : "th"}
                  </option>
                ))}
              </select>
              <p className="text-xs text-[var(--text-muted)]">
                If the month has fewer days, the task will be scheduled on the last day.
              </p>
            </div>
          )}

          {/* End date */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-[var(--text-secondary)]">
              End date <span className="text-[var(--text-muted)]">(optional)</span>
            </label>
            <input
              type="date"
              value={endDate ? endDate.split("T")[0] : ""}
              onChange={(e) =>
                setEndDate(e.target.value ? new Date(e.target.value).toISOString() : "")
              }
              min={new Date().toISOString().split("T")[0]}
              className="input-field w-full sm:w-48"
            />
          </div>

          {/* Preview */}
          <div className="p-3 rounded-lg bg-[var(--bg-secondary)] border border-[var(--border-primary)]">
            <p className="text-sm text-[var(--text-secondary)]">
              <span className="font-medium text-[var(--text-primary)]">Preview: </span>
              {describeRecurrence(type, interval, daysOfWeek, dayOfMonth)}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

function describeRecurrence(
  type: RecurrenceType,
  interval: number,
  daysOfWeek: number[],
  dayOfMonth: number
): string {
  const dayNames = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

  switch (type) {
    case "daily":
      return interval === 1 ? "Every day" : `Every ${interval} days`;
    case "weekly":
      const days = daysOfWeek.map((d) => dayNames[d]).join(", ");
      return interval === 1
        ? `Every ${days}`
        : `Every ${interval} weeks on ${days}`;
    case "monthly":
      const suffix =
        dayOfMonth === 1 || dayOfMonth === 21 || dayOfMonth === 31
          ? "st"
          : dayOfMonth === 2 || dayOfMonth === 22
          ? "nd"
          : dayOfMonth === 3 || dayOfMonth === 23
          ? "rd"
          : "th";
      return interval === 1
        ? `Every month on the ${dayOfMonth}${suffix}`
        : `Every ${interval} months on the ${dayOfMonth}${suffix}`;
    case "yearly":
      return interval === 1 ? "Every year" : `Every ${interval} years`;
    default:
      return "Custom recurrence";
  }
}

// Display component for showing recurrence info on task cards
interface RecurrenceIndicatorProps {
  recurrence: RecurrenceInfo;
  size?: "sm" | "md";
}

export function RecurrenceIndicator({
  recurrence,
  size = "sm",
}: RecurrenceIndicatorProps) {
  const sizeClasses = size === "sm" ? "text-xs gap-1" : "text-sm gap-1.5";
  const iconSize = size === "sm" ? "w-3.5 h-3.5" : "w-4 h-4";

  return (
    <span
      className={`flex items-center text-[var(--text-muted)] ${sizeClasses}`}
      title={`Repeats ${recurrence.type}`}
    >
      <svg
        className={iconSize}
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={2}
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
        />
      </svg>
      <span className="capitalize">{recurrence.type}</span>
      {recurrence.interval > 1 && (
        <span className="text-[var(--text-muted)]">
          (every {recurrence.interval})
        </span>
      )}
    </span>
  );
}
