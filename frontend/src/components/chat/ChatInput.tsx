"use client";

import { useRef, useState } from "react";

interface ChatInputProps {
  onSend: (message: string) => Promise<void>;
  isLoading: boolean;
}

const MAX_LENGTH = 2000;

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [charCount, setCharCount] = useState(0);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const textarea = textareaRef.current;
    if (!textarea) return;

    const message = textarea.value.trim();

    // Empty message validation (T015)
    if (!message) return;

    // Don't send while loading
    if (isLoading) return;

    textarea.value = "";
    setCharCount(0);
    await onSend(message);
  };

  // Enter to send, Shift+Enter for newline (T013)
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      const form = e.currentTarget.form;
      if (form) {
        form.requestSubmit();
      }
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setCharCount(e.target.value.length);
  };

  const isNearLimit = charCount > MAX_LENGTH * 0.9;
  const isAtLimit = charCount >= MAX_LENGTH;

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2">
      <div className="flex gap-3">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            name="message"
            placeholder="Type your message... (Shift+Enter for new line)"
            className="w-full bg-[var(--bg-tertiary)] border border-[var(--glass-border)] rounded-xl px-4 py-3 text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)]/50 resize-none pr-16"
            rows={1}
            maxLength={MAX_LENGTH}
            disabled={isLoading}
            onKeyDown={handleKeyDown}
            onChange={handleChange}
          />
          {/* Character count (T014) */}
          {charCount > 0 && (
            <span
              className={`absolute right-3 bottom-3 text-xs ${
                isAtLimit
                  ? "text-[var(--error)]"
                  : isNearLimit
                  ? "text-[var(--warning)]"
                  : "text-[var(--text-muted)]"
              }`}
            >
              {charCount}/{MAX_LENGTH}
            </span>
          )}
        </div>
        <button
          type="submit"
          disabled={isLoading || isAtLimit}
          className="px-4 py-3 bg-[var(--accent-primary)] text-white rounded-xl font-medium hover:bg-[var(--accent-primary)]/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-2"
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
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            />
          </svg>
          <span className="hidden sm:inline">Send</span>
        </button>
      </div>
    </form>
  );
}
