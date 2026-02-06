"use client";

import { forwardRef } from "react";

interface DatePickerProps {
  value: string;
  onChange: (value: string) => void;
  minDate?: string;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
  clearable?: boolean;
}

export const DatePicker = forwardRef<HTMLInputElement, DatePickerProps>(
  function DatePicker(
    {
      value,
      onChange,
      minDate,
      placeholder = "Select date",
      className = "",
      disabled = false,
      clearable = true,
    },
    ref
  ) {
    const handleClear = () => {
      onChange("");
    };

    return (
      <div className="relative">
        <input
          ref={ref}
          type="datetime-local"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          min={minDate}
          disabled={disabled}
          placeholder={placeholder}
          className={`
            input-field w-full pr-10
            ${disabled ? "opacity-50 cursor-not-allowed" : ""}
            ${className}
          `}
        />
        {clearable && value && !disabled && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-md
                       text-[var(--text-muted)] hover:text-[var(--text-primary)]
                       hover:bg-[var(--bg-tertiary)] transition-colors"
            aria-label="Clear date"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}
      </div>
    );
  }
);

export function formatDateForInput(date: Date | string | null): string {
  if (!date) return "";
  const d = typeof date === "string" ? new Date(date) : date;
  if (isNaN(d.getTime())) return "";

  // Format as YYYY-MM-DDTHH:mm for datetime-local input
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  const hours = String(d.getHours()).padStart(2, "0");
  const minutes = String(d.getMinutes()).padStart(2, "0");

  return `${year}-${month}-${day}T${hours}:${minutes}`;
}

export function formatDateForDisplay(date: string | null): string {
  if (!date) return "";
  const d = new Date(date);
  if (isNaN(d.getTime())) return "";

  return d.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function isOverdue(dueDate: string | null): boolean {
  if (!dueDate) return false;
  return new Date(dueDate) < new Date();
}
