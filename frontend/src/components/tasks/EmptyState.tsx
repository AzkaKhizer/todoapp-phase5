"use client";

interface EmptyStateProps {
  title?: string;
  message?: string;
}

export function EmptyState({
  title = "No tasks yet",
  message = "Create your first task to get started!",
}: EmptyStateProps) {
  return (
    <div className="glass-card rounded-2xl p-12 text-center">
      <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-[var(--accent-primary)]/20 to-[var(--accent-muted)]/10 mb-6">
        <svg
          className="w-10 h-10 text-[var(--accent-primary)]"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          strokeWidth={1.5}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
          />
        </svg>
      </div>
      <h3 className="text-xl font-semibold text-[var(--text-primary)] mb-2">
        {title}
      </h3>
      <p className="text-[var(--text-secondary)] max-w-sm mx-auto">
        {message}
      </p>
      <div className="mt-8 flex justify-center">
        <div className="flex items-center gap-2 text-sm text-[var(--text-muted)]">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 10l7-7m0 0l7 7m-7-7v18" />
          </svg>
          <span>Click the button above to add your first task</span>
        </div>
      </div>
    </div>
  );
}
