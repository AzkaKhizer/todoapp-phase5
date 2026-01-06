"use client";

import { TaskCard } from "./TaskCard";
import { EmptyState } from "./EmptyState";
import type { Task } from "@/lib/types";

interface TaskListProps {
  tasks: Task[];
  onToggle: (taskId: string) => Promise<void> | Promise<Task>;
  onEdit: (task: Task) => void;
  onDelete: (taskId: string) => Promise<void>;
}

export function TaskList({ tasks, onToggle, onEdit, onDelete }: TaskListProps) {
  if (tasks.length === 0) {
    return <EmptyState />;
  }

  // Separate pending and completed tasks
  const pendingTasks = tasks.filter((t) => !t.is_complete);
  const completedTasks = tasks.filter((t) => t.is_complete);

  return (
    <div className="space-y-6">
      {/* Pending Tasks */}
      {pendingTasks.length > 0 && (
        <div className="space-y-3">
          {pendingTasks.map((task, index) => (
            <div
              key={task.id}
              className="animate-slide-up"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <TaskCard
                task={task}
                onToggle={onToggle}
                onEdit={onEdit}
                onDelete={onDelete}
              />
            </div>
          ))}
        </div>
      )}

      {/* Completed Tasks Section */}
      {completedTasks.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-3 py-2">
            <div className="h-px flex-1 bg-gradient-to-r from-transparent via-[var(--glass-border)] to-transparent" />
            <span className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider">
              Completed ({completedTasks.length})
            </span>
            <div className="h-px flex-1 bg-gradient-to-r from-transparent via-[var(--glass-border)] to-transparent" />
          </div>
          {completedTasks.map((task, index) => (
            <div
              key={task.id}
              className="animate-slide-up"
              style={{ animationDelay: `${(pendingTasks.length + index) * 50}ms` }}
            >
              <TaskCard
                task={task}
                onToggle={onToggle}
                onEdit={onEdit}
                onDelete={onDelete}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
