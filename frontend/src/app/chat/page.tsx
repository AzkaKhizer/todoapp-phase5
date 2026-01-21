"use client";

import { useEffect } from "react";

import { ChatLayout, ChatWindow } from "@/components/chat";
import { Header } from "@/components/layout/Header";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { AuthProvider } from "@/contexts/AuthContext";
import { useChat } from "@/hooks/useChat";
import { useConversations } from "@/hooks/useConversations";

function ChatContent() {
  const {
    messages,
    conversationId,
    isLoading,
    error,
    sendMessage,
    clearError,
    startNewChat,
    retryLastMessage,
    loadConversation,
  } = useChat();

  const {
    conversations,
    isLoading: isLoadingConversations,
    refreshConversations,
    deleteConversation,
  } = useConversations();

  // Refresh conversations when a message is sent (new conversation might be created)
  useEffect(() => {
    if (conversationId) {
      refreshConversations();
    }
  }, [conversationId, refreshConversations]);

  // Check if there's a failed message for retry button
  const hasFailedMessage = messages.some(
    (m) => m.role === "user" && m.status === "error"
  );

  // Handle selecting a conversation from sidebar
  const handleSelectConversation = async (id: string) => {
    await loadConversation(id);
  };

  // Handle starting new chat
  const handleNewChat = () => {
    startNewChat();
  };

  // Handle deleting a conversation
  const handleDeleteConversation = async (id: string) => {
    await deleteConversation(id);
    // If the deleted conversation was active, start a new chat
    if (id === conversationId) {
      startNewChat();
    }
  };

  // Show loading spinner only on initial load with no messages
  if (isLoading && messages.length === 0 && !conversationId) {
    return (
      <div className="min-h-screen bg-gradient-radial flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-[var(--accent-primary)] border-t-transparent rounded-full animate-spin" />
          <p className="text-[var(--text-secondary)]">Loading chat...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-radial noise flex flex-col">
      <Header />

      <main className="flex-1 flex flex-col overflow-hidden">
        <ChatLayout
          conversations={conversations}
          activeConversationId={conversationId}
          onSelectConversation={handleSelectConversation}
          onDeleteConversation={handleDeleteConversation}
          onNewChat={handleNewChat}
          isLoadingConversations={isLoadingConversations}
        >
          <div className="flex-1 p-4 lg:p-6 flex flex-col">
            <ChatWindow
              messages={messages}
              isLoading={isLoading}
              error={error}
              onSend={sendMessage}
              onClearError={clearError}
              onRetry={retryLastMessage}
              hasFailedMessage={hasFailedMessage}
              conversationId={conversationId}
            />
          </div>
        </ChatLayout>
      </main>
    </div>
  );
}

export default function ChatPage() {
  return (
    <AuthProvider>
      <ProtectedRoute>
        <ChatContent />
      </ProtectedRoute>
    </AuthProvider>
  );
}
