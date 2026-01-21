"use client";

import { ChatInput } from "./ChatInput";
import { MessageList } from "./MessageList";
import { NewChatButton } from "./NewChatButton";

import type { LocalChatMessage } from "@/lib/types";

interface ChatWindowProps {
  messages: LocalChatMessage[];
  isLoading: boolean;
  error: string | null;
  onSend: (message: string) => Promise<void>;
  onClearError: () => void;
  onRetry?: () => Promise<void>;
  hasFailedMessage?: boolean;
  onNewChat?: () => void;
  conversationId?: string | null;
}

export function ChatWindow({
  messages,
  isLoading,
  error,
  onSend,
  onClearError,
  onRetry,
  hasFailedMessage,
  onNewChat,
  conversationId,
}: ChatWindowProps) {
  return (
    <div className="flex-1 glass-card rounded-xl flex flex-col overflow-hidden animate-slide-up">
      {/* Header with New Chat button (T032) */}
      {onNewChat && (
        <div className="p-4 border-b border-[var(--glass-border)] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <svg
              className="w-5 h-5 text-[var(--accent-primary)]"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
            <span className="font-medium text-[var(--text-primary)]">
              {conversationId ? "Conversation" : "New Chat"}
            </span>
          </div>
          <NewChatButton onClick={onNewChat} disabled={isLoading} />
        </div>
      )}

      {/* Error Banner with Retry (T027) */}
      {error && (
        <div className="p-4 bg-[var(--error)]/10 border-b border-[var(--error)]/20 text-[var(--error)] text-sm flex items-center justify-between">
          <div className="flex items-center gap-3">
            <svg
              className="w-5 h-5 flex-shrink-0"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <span>{error}</span>
          </div>
          <div className="flex items-center gap-2">
            {/* Retry button (T027) */}
            {hasFailedMessage && onRetry && (
              <button
                onClick={onRetry}
                disabled={isLoading}
                className="px-3 py-1 bg-[var(--error)] text-white rounded-lg text-sm font-medium hover:bg-[var(--error)]/90 disabled:opacity-50 transition-colors flex items-center gap-1"
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
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
                Retry
              </button>
            )}
            <button
              onClick={onClearError}
              className="text-[var(--error)] hover:text-[var(--error)]/80 transition-colors"
            >
              <svg
                className="w-5 h-5"
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
          </div>
        </div>
      )}

      {/* Messages Area */}
      <MessageList messages={messages} isLoading={isLoading} />

      {/* Input Area */}
      <div className="border-t border-[var(--glass-border)] p-4">
        <ChatInput onSend={onSend} isLoading={isLoading} />
      </div>
    </div>
  );
}
