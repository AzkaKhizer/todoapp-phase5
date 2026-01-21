"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { MessageBubble } from "./MessageBubble";

import type { LocalChatMessage } from "@/lib/types";

interface MessageListProps {
  messages: LocalChatMessage[];
  isLoading: boolean;
}

export function MessageList({ messages, isLoading }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isAtBottom, setIsAtBottom] = useState(true);
  const [hasNewMessage, setHasNewMessage] = useState(false);
  const prevMessageCount = useRef(messages.length);

  // Check if user is at or near bottom (T020)
  const checkIfAtBottom = useCallback(() => {
    const container = containerRef.current;
    if (!container) return true;

    const threshold = 100; // pixels from bottom
    const { scrollTop, scrollHeight, clientHeight } = container;
    return scrollHeight - scrollTop - clientHeight < threshold;
  }, []);

  // Handle scroll events to track position (T020)
  const handleScroll = useCallback(() => {
    const atBottom = checkIfAtBottom();
    setIsAtBottom(atBottom);
    if (atBottom) {
      setHasNewMessage(false);
    }
  }, [checkIfAtBottom]);

  // Smart auto-scroll: only when at bottom (T020)
  useEffect(() => {
    const newMessageCount = messages.length;
    const hadNewMessages = newMessageCount > prevMessageCount.current;
    prevMessageCount.current = newMessageCount;

    if (hadNewMessages) {
      if (isAtBottom) {
        // User is at bottom, scroll smoothly
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
      } else {
        // User scrolled up, show new message indicator (T021)
        setHasNewMessage(true);
      }
    }
  }, [messages, isAtBottom]);

  // Also scroll when loading indicator appears/disappears
  useEffect(() => {
    if (isAtBottom && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [isLoading, isAtBottom]);

  // Scroll to bottom when clicking "new message" indicator
  const scrollToBottom = useCallback(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    setHasNewMessage(false);
    setIsAtBottom(true);
  }, []);

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-center p-6">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[var(--accent-secondary)] to-[var(--accent-muted)] flex items-center justify-center mb-4">
          <svg
            className="w-8 h-8 text-[var(--bg-primary)]"
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
        </div>
        <h2 className="text-xl font-semibold mb-2">AI Task Assistant</h2>
        <p className="text-[var(--text-muted)] max-w-md">
          Ask me to manage your tasks! Try &quot;Show my tasks&quot;, &quot;Add
          task: Review PR&quot;, or &quot;Complete task 1&quot;.
        </p>
      </div>
    );
  }

  return (
    <div className="relative flex-1 flex flex-col overflow-hidden">
      <div
        ref={containerRef}
        className="flex-1 p-6 overflow-y-auto"
        onScroll={handleScroll}
      >
        <div className="space-y-4">
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          {isLoading && <LoadingIndicator />}
          <div ref={bottomRef} />
        </div>
      </div>

      {/* New message indicator (T021) */}
      {hasNewMessage && (
        <button
          onClick={scrollToBottom}
          className="absolute bottom-4 left-1/2 -translate-x-1/2 px-4 py-2 bg-[var(--accent-primary)] text-white text-sm rounded-full shadow-lg hover:bg-[var(--accent-primary)]/90 transition-all duration-200 flex items-center gap-2 animate-slide-up"
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
              d="M19 14l-7 7m0 0l-7-7m7 7V3"
            />
          </svg>
          New message
        </button>
      )}
    </div>
  );
}

function LoadingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bg-[var(--bg-tertiary)] rounded-2xl px-4 py-3">
        <div className="flex items-center gap-2">
          <div
            className="w-2 h-2 bg-[var(--text-muted)] rounded-full animate-bounce"
            style={{ animationDelay: "0ms" }}
          />
          <div
            className="w-2 h-2 bg-[var(--text-muted)] rounded-full animate-bounce"
            style={{ animationDelay: "150ms" }}
          />
          <div
            className="w-2 h-2 bg-[var(--text-muted)] rounded-full animate-bounce"
            style={{ animationDelay: "300ms" }}
          />
        </div>
      </div>
    </div>
  );
}
