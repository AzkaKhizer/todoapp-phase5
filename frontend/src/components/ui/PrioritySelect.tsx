"use client";

import { forwardRef } from "react";
import type { TaskPriority } from "@/lib/types";

interface PrioritySelectProps {
  value: TaskPriority;
  onChange: (value: TaskPriority) => void;
  className?: string;
  disabled?: boolean;
}

const PRIORITY_OPTIONS: { value: TaskPriority; label: string; color: string }[] = [
  { value: "low", label: "Low", color: "bg-gray-500" },
  { value: "medium", label: "Medium", color: "bg-blue-500" },
  { value: "high", label: "High", color: "bg-orange-500" },
  { value: "urgent", label: "Urgent", color: "bg-red-500" },
];

export const PrioritySelect = forwardRef<HTMLSelectElement, PrioritySelectProps>(
  function PrioritySelect({ value, onChange, className = "", disabled = false }, ref) {
    return (
      <div className="relative">
        <select
          ref={ref}
          value={value}
          onChange={(e) => onChange(e.target.value as TaskPriority)}
          disabled={disabled}
          className={`
            input-field w-full appearance-none cursor-pointer pr-10
            ${disabled ? "opacity-50 cursor-not-allowed" : ""}
            ${className}
          `}
        >
          {PRIORITY_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
          <svg
            className="w-4 h-4 text-[var(--text-muted)]"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>
    );
  }
);

export function PriorityBadge({
  priority,
  size = "sm",
}: {
  priority: TaskPriority;
  size?: "sm" | "md";
}) {
  const option = PRIORITY_OPTIONS.find((o) => o.value === priority);
  if (!option) return null;

  const sizeClasses = size === "sm" ? "text-xs px-2 py-0.5" : "text-sm px-2.5 py-1";

  return (
    <span
      className={`
        inline-flex items-center gap-1 rounded-full font-medium
        ${sizeClasses}
        ${getPriorityStyles(priority)}
      `}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${option.color}`} />
      {option.label}
    </span>
  );
}

export function getPriorityStyles(priority: TaskPriority): string {
  switch (priority) {
    case "low":
      return "bg-gray-500/10 text-gray-400 border border-gray-500/20";
    case "medium":
      return "bg-blue-500/10 text-blue-400 border border-blue-500/20";
    case "high":
      return "bg-orange-500/10 text-orange-400 border border-orange-500/20";
    case "urgent":
      return "bg-red-500/10 text-red-400 border border-red-500/20";
    default:
      return "bg-gray-500/10 text-gray-400 border border-gray-500/20";
  }
}

export function getPriorityColor(priority: TaskPriority): string {
  switch (priority) {
    case "low":
      return "#6B7280";
    case "medium":
      return "#3B82F6";
    case "high":
      return "#F97316";
    case "urgent":
      return "#EF4444";
    default:
      return "#6B7280";
  }
}
