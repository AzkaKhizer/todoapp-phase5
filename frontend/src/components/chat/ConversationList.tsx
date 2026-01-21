"use client";

import type { Conversation } from "@/lib/types";

interface ConversationListProps {
  conversations: Conversation[];
  activeConversationId: string | null;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
  isLoading: boolean;
}

// Format date for display
function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } else if (diffDays === 1) {
    return "Yesterday";
  } else if (diffDays < 7) {
    return date.toLocaleDateString([], { weekday: "short" });
  } else {
    return date.toLocaleDateString([], { month: "short", day: "numeric" });
  }
}

export function ConversationList({
  conversations,
  activeConversationId,
  onSelect,
  onDelete,
  isLoading,
}: ConversationListProps) {
  if (isLoading) {
    return (
      <div className="p-4 space-y-3">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-16 bg-[var(--bg-tertiary)] rounded-lg animate-pulse"
          />
        ))}
      </div>
    );
  }

  if (conversations.length === 0) {
    return (
      <div className="p-4 text-center text-[var(--text-muted)] text-sm">
        <p>No conversations yet.</p>
        <p className="mt-1">Start a new chat to get started!</p>
      </div>
    );
  }

  return (
    <div className="p-2 space-y-1">
      {conversations.map((conversation) => {
        const isActive = conversation.id === activeConversationId;
        return (
          <div
            key={conversation.id}
            className={`group w-full text-left p-3 rounded-lg transition-all duration-200 ${
              isActive
                ? "bg-[var(--accent-primary)]/10 border border-[var(--accent-primary)]/30"
                : "hover:bg-[var(--bg-tertiary)] border border-transparent"
            }`}
          >
            <div className="flex items-start justify-between gap-2">
              <button
                onClick={() => onSelect(conversation.id)}
                className="flex-1 min-w-0 text-left"
              >
                <p
                  className={`text-sm font-medium truncate ${
                    isActive
                      ? "text-[var(--accent-primary)]"
                      : "text-[var(--text-primary)]"
                  }`}
                >
                  {conversation.title || "New conversation"}
                </p>
                <p className="text-xs text-[var(--text-muted)] mt-1">
                  {formatDate(conversation.updated_at)}
                </p>
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  if (confirm("Delete this conversation?")) {
                    onDelete(conversation.id);
                  }
                }}
                className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-[var(--error)]/10 text-[var(--text-muted)] hover:text-[var(--error)] transition-all"
                title="Delete conversation"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
