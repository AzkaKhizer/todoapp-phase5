"use client";

import { useCallback, useState } from "react";

import { useSession } from "@/lib/auth-client";
import { api, ApiError } from "@/lib/api";

import type {
  ChatRequest,
  ChatResponse,
  ConversationDetailResponse,
  LocalChatMessage,
} from "@/lib/types";

// Simple unique ID generator (no external dependency)
const generateId = () =>
  typeof crypto !== "undefined" && crypto.randomUUID
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;

interface UseChatState {
  messages: LocalChatMessage[];
  conversationId: string | null;
  isLoading: boolean;
  error: string | null;
}

interface UseChatReturn extends UseChatState {
  sendMessage: (message: string) => Promise<void>;
  loadConversation: (id: string) => Promise<void>;
  startNewChat: () => void;
  clearError: () => void;
  retryLastMessage: () => Promise<void>;
}

const ERROR_MESSAGES: Record<number, string> = {
  401: "Please log in to continue.",
  429: "Too many requests. Please wait a moment.",
  503: "AI service is temporarily unavailable.",
  504: "Request timed out. Try a shorter message.",
};

export function useChat(): UseChatReturn {
  const { data: session } = useSession();
  const [state, setState] = useState<UseChatState>({
    messages: [],
    conversationId: null,
    isLoading: false,
    error: null,
  });

  const sendMessage = useCallback(
    async (message: string) => {
      if (!session?.user) {
        setState((prev) => ({ ...prev, error: "Please log in to continue." }));
        return;
      }

      const trimmedMessage = message.trim();
      if (!trimmedMessage) {
        setState((prev) => ({ ...prev, error: "Message cannot be empty." }));
        return;
      }

      if (trimmedMessage.length > 2000) {
        setState((prev) => ({
          ...prev,
          error: "Message is too long. Maximum 2000 characters.",
        }));
        return;
      }

      // Create optimistic user message
      const userMessage: LocalChatMessage = {
        id: generateId(),
        role: "user",
        content: trimmedMessage,
        created_at: new Date().toISOString(),
        status: "pending",
      };

      // Add user message and set loading
      setState((prev) => ({
        ...prev,
        messages: [...prev.messages, userMessage],
        isLoading: true,
        error: null,
      }));

      try {
        const request: ChatRequest = {
          message: trimmedMessage,
          conversation_id: state.conversationId || undefined,
        };

        const response = await api.post<ChatResponse>("/chat", request, true);

        // Create assistant message from response
        const assistantMessage: LocalChatMessage = {
          id: generateId(),
          role: "assistant",
          content: response.message,
          created_at: new Date().toISOString(),
          status: "sent",
        };

        setState((prev) => ({
          ...prev,
          messages: prev.messages.map((m) =>
            m.id === userMessage.id ? { ...m, status: "sent" as const } : m
          ).concat(assistantMessage),
          conversationId: response.conversation_id,
          isLoading: false,
        }));
      } catch (err) {
        console.error("Chat error:", err);

        // Mark user message as error
        setState((prev) => ({
          ...prev,
          messages: prev.messages.map((m) =>
            m.id === userMessage.id ? { ...m, status: "error" as const } : m
          ),
          isLoading: false,
          error:
            err instanceof ApiError
              ? ERROR_MESSAGES[err.status] || err.message
              : "Failed to send message. Please try again.",
        }));
      }
    },
    [session?.user, state.conversationId]
  );

  const loadConversation = useCallback(
    async (id: string) => {
      if (!session?.user) {
        setState((prev) => ({ ...prev, error: "Please log in to continue." }));
        return;
      }

      setState((prev) => ({ ...prev, isLoading: true, error: null }));

      try {
        const response = await api.get<ConversationDetailResponse>(
          `/chat/conversations/${id}`,
          true
        );

        const messages: LocalChatMessage[] = response.messages.map((m) => ({
          ...m,
          status: "sent" as const,
        }));

        setState({
          messages,
          conversationId: id,
          isLoading: false,
          error: null,
        });
      } catch (err) {
        console.error("Load conversation error:", err);
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error:
            err instanceof ApiError
              ? err.message
              : "Failed to load conversation.",
        }));
      }
    },
    [session?.user]
  );

  const startNewChat = useCallback(() => {
    setState({
      messages: [],
      conversationId: null,
      isLoading: false,
      error: null,
    });
  }, []);

  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  const retryLastMessage = useCallback(async () => {
    // Find the last failed user message
    const lastFailedMessage = [...state.messages]
      .reverse()
      .find((m) => m.role === "user" && m.status === "error");

    if (!lastFailedMessage) return;

    // Remove the failed message and retry
    setState((prev) => ({
      ...prev,
      messages: prev.messages.filter((m) => m.id !== lastFailedMessage.id),
      error: null,
    }));

    await sendMessage(lastFailedMessage.content);
  }, [state.messages, sendMessage]);

  return {
    ...state,
    sendMessage,
    loadConversation,
    startNewChat,
    clearError,
    retryLastMessage,
  };
}
