"use client";

import type { LocalChatMessage } from "@/lib/types";

interface MessageBubbleProps {
  message: LocalChatMessage;
  showTimestamp?: boolean;
}

// Format timestamp for display (T019)
function formatTime(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export function MessageBubble({ message, showTimestamp = true }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const isPending = message.status === "pending";
  const isError = message.status === "error";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className="flex flex-col gap-1">
        <div
          className={`max-w-[80%] rounded-2xl px-4 py-3 ${
            isUser
              ? "bg-[var(--accent-primary)] text-white"
              : "bg-[var(--bg-tertiary)] text-[var(--text-primary)]"
          } ${isPending ? "opacity-70" : ""} ${
            isError ? "border border-[var(--error)]" : ""
          }`}
        >
          <p className="whitespace-pre-wrap">{message.content}</p>
          {isError && (
            <p className="text-xs text-[var(--error)] mt-1">Failed to send</p>
          )}
        </div>
        {/* Timestamp display (T019) */}
        {showTimestamp && !isPending && (
          <span
            className={`text-xs text-[var(--text-muted)] ${
              isUser ? "text-right" : "text-left"
            }`}
          >
            {formatTime(message.created_at)}
          </span>
        )}
      </div>
    </div>
  );
}
