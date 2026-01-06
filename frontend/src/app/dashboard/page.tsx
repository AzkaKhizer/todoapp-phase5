"use client";

import { useState } from "react";

import { TaskForm } from "@/components/forms/TaskForm";
import { Header } from "@/components/layout/Header";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { EditTaskModal } from "@/components/tasks/EditTaskModal";
import { TaskList } from "@/components/tasks/TaskList";
import { AuthProvider } from "@/contexts/AuthContext";
import { useTasks } from "@/hooks/useTasks";
import type { Task } from "@/lib/types";

function DashboardContent() {
  const {
    tasks,
    isLoading,
    error,
    createTask,
    updateTask,
    deleteTask,
    toggleTask,
  } = useTasks();

  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [showForm, setShowForm] = useState(false);

  const handleCreateTask = async (data: {
    title: string;
    description: string;
  }) => {
    await createTask(data);
    setShowForm(false);
  };

  const handleEditTask = (task: Task) => {
    setEditingTask(task);
  };

  const handleSaveEdit = async (
    taskId: string,
    data: { title: string; description: string }
  ) => {
    await updateTask(taskId, data);
  };

  const completedCount = tasks.filter((t) => t.is_complete).length;
  const pendingCount = tasks.length - completedCount;

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-radial flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-[var(--accent-primary)] border-t-transparent rounded-full animate-spin" />
          <p className="text-[var(--text-secondary)]">Loading your tasks...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-radial noise">
      <Header />

      <main className="max-w-4xl mx-auto px-6 py-8">
        {error && (
          <div className="mb-6 p-4 rounded-lg bg-[var(--error)]/10 border border-[var(--error)]/20 text-[var(--error)] text-sm flex items-center gap-3 animate-slide-up">
            <svg className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            {error}
          </div>
        )}

        {/* Stats Section */}
        <div className="grid grid-cols-3 gap-4 mb-8 animate-slide-up">
          <div className="glass-card rounded-xl p-5 text-center">
            <p className="text-3xl font-bold text-gradient">{tasks.length}</p>
            <p className="text-sm text-[var(--text-muted)] mt-1">Total Tasks</p>
          </div>
          <div className="glass-card rounded-xl p-5 text-center">
            <p className="text-3xl font-bold text-[var(--warning)]">{pendingCount}</p>
            <p className="text-sm text-[var(--text-muted)] mt-1">Pending</p>
          </div>
          <div className="glass-card rounded-xl p-5 text-center">
            <p className="text-3xl font-bold text-[var(--success)]">{completedCount}</p>
            <p className="text-sm text-[var(--text-muted)] mt-1">Completed</p>
          </div>
        </div>

        {/* Add Task Section */}
        <div className="mb-8 animate-slide-up delay-100">
          {!showForm ? (
            <button
              onClick={() => setShowForm(true)}
              className="w-full glass-card rounded-xl p-5 flex items-center justify-center gap-3 text-[var(--text-secondary)] hover:text-[var(--accent-primary)] hover:border-[var(--accent-primary)]/30 transition-all duration-300 group"
            >
              <div className="w-10 h-10 rounded-lg bg-[var(--bg-tertiary)] flex items-center justify-center group-hover:bg-[var(--accent-primary)]/10 transition-colors">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                </svg>
              </div>
              <span className="font-medium">Add a new task</span>
            </button>
          ) : (
            <div className="card-elevated rounded-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold">Create New Task</h2>
                <button
                  onClick={() => setShowForm(false)}
                  className="text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <TaskForm onSubmit={handleCreateTask} />
            </div>
          )}
        </div>

        {/* Task List */}
        <div className="animate-slide-up delay-200">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold">
              Your Tasks
              <span className="ml-2 text-sm font-normal text-[var(--text-muted)]">
                ({tasks.length})
              </span>
            </h2>
          </div>
          <TaskList
            tasks={tasks}
            onToggle={toggleTask}
            onEdit={handleEditTask}
            onDelete={deleteTask}
          />
        </div>

        {/* Edit Modal */}
        <EditTaskModal
          task={editingTask}
          isOpen={!!editingTask}
          onClose={() => setEditingTask(null)}
          onSave={handleSaveEdit}
        />
      </main>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <AuthProvider>
      <ProtectedRoute>
        <DashboardContent />
      </ProtectedRoute>
    </AuthProvider>
  );
}
