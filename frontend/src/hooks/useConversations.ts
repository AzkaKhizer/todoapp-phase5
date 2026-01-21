"use client";

import { useCallback, useEffect, useState } from "react";

import { useSession } from "@/lib/auth-client";
import { api, ApiError } from "@/lib/api";

import type { Conversation, ConversationListResponse } from "@/lib/types";

interface UseConversationsState {
  conversations: Conversation[];
  total: number;
  isLoading: boolean;
  error: string | null;
}

interface UseConversationsReturn extends UseConversationsState {
  fetchConversations: () => Promise<void>;
  refreshConversations: () => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
  clearError: () => void;
}

export function useConversations(): UseConversationsReturn {
  const { data: session, isPending: isSessionLoading } = useSession();
  const [state, setState] = useState<UseConversationsState>({
    conversations: [],
    total: 0,
    isLoading: false,
    error: null,
  });

  // Fetch conversations from the API (T003 - Session guard added)
  const fetchConversations = useCallback(async () => {
    // Guard: Don't fetch if session is still loading or user not authenticated
    if (isSessionLoading || !session?.user) {
      return;
    }

    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await api.get<ConversationListResponse>(
        "/chat/conversations",
        true
      );

      setState({
        conversations: response.conversations,
        total: response.total,
        isLoading: false,
        error: null,
      });
    } catch (err) {
      console.error("Fetch conversations error:", err);
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error:
          err instanceof ApiError
            ? err.message
            : "Failed to load conversations.",
      }));
    }
  }, [session?.user, isSessionLoading]);

  // Refresh conversations (alias for refetch)
  const refreshConversations = useCallback(async () => {
    await fetchConversations();
  }, [fetchConversations]);

  // Delete a conversation
  const deleteConversation = useCallback(async (id: string) => {
    try {
      await api.delete(`/chat/conversations/${id}`, true);
      setState((prev) => ({
        ...prev,
        conversations: prev.conversations.filter((c) => c.id !== id),
        total: prev.total - 1,
      }));
    } catch (err) {
      console.error("Delete conversation error:", err);
      setState((prev) => ({
        ...prev,
        error: err instanceof ApiError ? err.message : "Failed to delete conversation.",
      }));
    }
  }, []);

  // Clear error
  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: null }));
  }, []);

  // Auto-fetch on mount when user is authenticated and session is ready (T003)
  useEffect(() => {
    // Only fetch when session loading is complete and user is authenticated
    if (!isSessionLoading && session?.user) {
      fetchConversations();
    }
  }, [session?.user, isSessionLoading, fetchConversations]);

  return {
    ...state,
    fetchConversations,
    refreshConversations,
    deleteConversation,
    clearError,
  };
}
