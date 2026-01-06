"use client";

import { useState } from "react";

import type { Task } from "@/lib/types";

interface TaskCardProps {
  task: Task;
  onToggle: (taskId: string) => Promise<void> | Promise<Task>;
  onEdit: (task: Task) => void;
  onDelete: (taskId: string) => Promise<void>;
}

export function TaskCard({ task, onToggle, onEdit, onDelete }: TaskCardProps) {
  const [isToggling, setIsToggling] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const handleToggle = async () => {
    setIsToggling(true);
    try {
      await onToggle(task.id);
    } finally {
      setIsToggling(false);
    }
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await onDelete(task.id);
    } finally {
      setIsDeleting(false);
      setShowConfirm(false);
    }
  };

  return (
    <div
      className={`
        glass-card rounded-xl p-5 transition-all duration-300 hover:border-[var(--accent-primary)]/20
        ${task.is_complete ? "opacity-60" : ""}
      `}
    >
      <div className="flex items-start gap-4">
        {/* Checkbox */}
        <button
          onClick={handleToggle}
          disabled={isToggling}
          className={`
            mt-0.5 flex-shrink-0 w-6 h-6 rounded-lg border-2
            flex items-center justify-center transition-all duration-200
            ${
              task.is_complete
                ? "bg-[var(--success)] border-[var(--success)]"
                : "border-[var(--text-muted)] hover:border-[var(--accent-primary)]"
            }
            ${isToggling ? "opacity-50 scale-95" : "hover:scale-105"}
          `}
          aria-label={task.is_complete ? "Mark as incomplete" : "Mark as complete"}
        >
          {task.is_complete && (
            <svg className="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          )}
        </button>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <h3
            className={`
              text-base font-medium transition-all duration-200
              ${task.is_complete ? "text-[var(--text-muted)] line-through" : "text-[var(--text-primary)]"}
            `}
          >
            {task.title}
          </h3>
          {task.description && (
            <p
              className={`
                mt-1.5 text-sm leading-relaxed
                ${task.is_complete ? "text-[var(--text-muted)]" : "text-[var(--text-secondary)]"}
              `}
            >
              {task.description}
            </p>
          )}
        </div>

        {/* Actions */}
        <div className="flex-shrink-0 flex items-center gap-1">
          <button
            onClick={() => onEdit(task)}
            className="p-2 rounded-lg text-[var(--text-muted)] hover:text-[var(--accent-primary)] hover:bg-[var(--accent-primary)]/10 transition-all duration-200"
            aria-label="Edit task"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>

          {showConfirm ? (
            <div className="flex items-center gap-1 ml-1">
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className="px-3 py-1.5 rounded-lg text-sm font-medium bg-[var(--error)] text-white hover:bg-[var(--error)]/80 transition-all duration-200 disabled:opacity-50"
              >
                {isDeleting ? "..." : "Delete"}
              </button>
              <button
                onClick={() => setShowConfirm(false)}
                className="px-3 py-1.5 rounded-lg text-sm font-medium text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)] transition-all duration-200"
              >
                Cancel
              </button>
            </div>
          ) : (
            <button
              onClick={() => setShowConfirm(true)}
              className="p-2 rounded-lg text-[var(--text-muted)] hover:text-[var(--error)] hover:bg-[var(--error)]/10 transition-all duration-200"
              aria-label="Delete task"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
