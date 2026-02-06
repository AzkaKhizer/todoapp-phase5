"use client";

import { useState, useEffect } from "react";
import { useForm, Controller } from "react-hook-form";
import type { TaskPriority, TagWithCount } from "@/lib/types";
import { DatePicker, formatDateForInput } from "@/components/ui/DatePicker";
import { PrioritySelect } from "@/components/ui/PrioritySelect";
import { TagInput } from "@/components/ui/TagInput";

interface TaskFormData {
  title: string;
  description: string;
  due_date: string;
  priority: TaskPriority;
  tags: string[];
  reminder_offset_minutes: number | null;
}

interface TaskFormProps {
  onSubmit: (data: TaskFormData) => Promise<void>;
  initialData?: Partial<TaskFormData>;
  submitLabel?: string;
  availableTags?: TagWithCount[];
}

const REMINDER_OPTIONS = [
  { value: null, label: "No reminder" },
  { value: 15, label: "15 minutes before" },
  { value: 30, label: "30 minutes before" },
  { value: 60, label: "1 hour before" },
  { value: 1440, label: "1 day before" },
  { value: 10080, label: "1 week before" },
];

export function TaskForm({
  onSubmit,
  initialData,
  submitLabel = "Add Task",
  availableTags = [],
}: TaskFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const defaultValues: TaskFormData = {
    title: initialData?.title || "",
    description: initialData?.description || "",
    due_date: initialData?.due_date ? formatDateForInput(initialData.due_date) : "",
    priority: initialData?.priority || "medium",
    tags: initialData?.tags || [],
    reminder_offset_minutes: initialData?.reminder_offset_minutes ?? null,
  };

  const {
    register,
    handleSubmit,
    reset,
    control,
    watch,
    formState: { errors },
  } = useForm<TaskFormData>({
    defaultValues,
  });

  const dueDate = watch("due_date");

  // Show advanced options if any are set
  useEffect(() => {
    if (initialData?.due_date || initialData?.tags?.length || initialData?.reminder_offset_minutes) {
      setShowAdvanced(true);
    }
  }, [initialData]);

  const handleFormSubmit = async (data: TaskFormData) => {
    setIsSubmitting(true);
    setError(null);

    try {
      await onSubmit(data);
      if (!initialData?.title) {
        reset(defaultValues);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-5">
      {error && (
        <div className="p-4 rounded-lg bg-[var(--error)]/10 border border-[var(--error)]/20 text-[var(--error)] text-sm flex items-center gap-3">
          <svg className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          {error}
        </div>
      )}

      <div className="space-y-2">
        <label className="block text-sm font-medium text-[var(--text-secondary)]">
          Title
        </label>
        <input
          type="text"
          placeholder="What needs to be done?"
          className="input-field"
          {...register("title", {
            required: "Title is required",
            maxLength: {
              value: 200,
              message: "Title must be 200 characters or less",
            },
          })}
        />
        {errors.title && (
          <p className="text-sm text-[var(--error)] flex items-center gap-1.5">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            {errors.title.message}
          </p>
        )}
      </div>

      <div className="space-y-2">
        <label className="block text-sm font-medium text-[var(--text-secondary)]">
          Description <span className="text-[var(--text-muted)]">(optional)</span>
        </label>
        <textarea
          rows={3}
          placeholder="Add more details..."
          className="input-field resize-none"
          {...register("description", {
            maxLength: {
              value: 2000,
              message: "Description must be 2000 characters or less",
            },
          })}
        />
        {errors.description && (
          <p className="text-sm text-[var(--error)] flex items-center gap-1.5">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            {errors.description.message}
          </p>
        )}
      </div>

      {/* Priority field - always visible */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-[var(--text-secondary)]">
          Priority
        </label>
        <Controller
          name="priority"
          control={control}
          render={({ field }) => (
            <PrioritySelect
              value={field.value}
              onChange={field.onChange}
            />
          )}
        />
      </div>

      {/* Advanced options toggle */}
      <button
        type="button"
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="flex items-center gap-2 text-sm text-[var(--accent-primary)] hover:underline"
      >
        <svg
          className={`w-4 h-4 transition-transform ${showAdvanced ? "rotate-90" : ""}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
        </svg>
        {showAdvanced ? "Hide" : "Show"} advanced options
      </button>

      {/* Advanced options */}
      {showAdvanced && (
        <div className="space-y-4 pt-2 border-t border-[var(--border-primary)]">
          {/* Due date */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-[var(--text-secondary)]">
              Due Date <span className="text-[var(--text-muted)]">(optional)</span>
            </label>
            <Controller
              name="due_date"
              control={control}
              render={({ field }) => (
                <DatePicker
                  value={field.value}
                  onChange={field.onChange}
                  minDate={formatDateForInput(new Date())}
                />
              )}
            />
          </div>

          {/* Reminder - only show if due date is set */}
          {dueDate && (
            <div className="space-y-2">
              <label className="block text-sm font-medium text-[var(--text-secondary)]">
                Reminder
              </label>
              <Controller
                name="reminder_offset_minutes"
                control={control}
                render={({ field }) => (
                  <select
                    value={field.value ?? ""}
                    onChange={(e) => {
                      const val = e.target.value;
                      field.onChange(val === "" ? null : Number(val));
                    }}
                    className="input-field w-full"
                  >
                    {REMINDER_OPTIONS.map((opt) => (
                      <option key={opt.label} value={opt.value ?? ""}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                )}
              />
            </div>
          )}

          {/* Tags */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-[var(--text-secondary)]">
              Tags <span className="text-[var(--text-muted)]">(optional)</span>
            </label>
            <Controller
              name="tags"
              control={control}
              render={({ field }) => (
                <TagInput
                  value={field.value}
                  onChange={field.onChange}
                  suggestions={availableTags}
                  placeholder="Add tags..."
                />
              )}
            />
          </div>
        </div>
      )}

      <button
        type="submit"
        disabled={isSubmitting}
        className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span className="flex items-center justify-center gap-2">
          {isSubmitting ? (
            <>
              <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Processing...
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
              </svg>
              {submitLabel}
            </>
          )}
        </span>
      </button>
    </form>
  );
}
