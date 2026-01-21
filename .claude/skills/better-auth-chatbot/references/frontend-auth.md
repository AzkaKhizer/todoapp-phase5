# Frontend Authentication

Token handling and API authentication for Next.js with Better Auth.

## Auth Client Setup

```typescript
// frontend/src/lib/auth-client.ts
import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
});

export const {
  signIn,
  signUp,
  signOut,
  useSession,
  getSession,
} = authClient;
```

## Getting JWT Token

```typescript
// frontend/src/lib/auth.ts
import { authClient } from './auth-client';

/**
 * Get JWT token for API requests.
 * Fetches from /api/auth/token endpoint after session verification.
 */
export async function getAuthToken(): Promise<string | null> {
  try {
    const session = await authClient.getSession();
    if (!session?.user) {
      return null;
    }

    // Request JWT from backend
    const response = await fetch('/api/auth/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: session.user.id,
        email: session.user.email,
        name: session.user.name,
      }),
    });

    if (!response.ok) {
      return null;
    }

    const data = await response.json();
    return data.token;
  } catch (error) {
    console.error('Failed to get auth token:', error);
    return null;
  }
}
```

## API Client with Auth

```typescript
// frontend/src/lib/api-client.ts
import { getAuthToken } from './auth';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Make authenticated API request.
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getAuthToken();

  if (!token) {
    throw new Error('Not authenticated');
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (response.status === 401) {
    throw new Error('Authentication expired');
  }

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}
```

## Chat API Client

```typescript
// frontend/src/lib/chat-api.ts
import { apiRequest } from './api-client';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatResponse {
  message: string;
  conversation_id: string;
}

export interface Conversation {
  id: string;
  title: string | null;
  created_at: string;
  messages?: ChatMessage[];
}

export const chatApi = {
  /**
   * Send a chat message.
   */
  async send(message: string, conversationId?: string | null): Promise<ChatResponse> {
    return apiRequest<ChatResponse>('/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
      }),
    });
  },

  /**
   * List user's conversations.
   */
  async getConversations(): Promise<{ conversations: Conversation[] }> {
    return apiRequest('/api/chat/conversations');
  },

  /**
   * Get a specific conversation with messages.
   */
  async getConversation(id: string): Promise<Conversation> {
    return apiRequest(`/api/chat/conversations/${id}`);
  },

  /**
   * Delete a conversation.
   */
  async deleteConversation(id: string): Promise<void> {
    await apiRequest(`/api/chat/conversations/${id}`, {
      method: 'DELETE',
    });
  },
};
```

## useChat Hook with Auth

```typescript
// frontend/src/hooks/useChat.ts
import { useState, useCallback } from 'react';
import { useSession } from '@/lib/auth-client';
import { chatApi, ChatMessage, ChatResponse } from '@/lib/chat-api';

export function useChat(initialConversationId?: string) {
  const { data: session } = useSession();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(
    initialConversationId || null
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (content: string) => {
    if (!session?.user) {
      setError('Please log in to use the chat');
      return;
    }

    if (!content.trim()) return;

    setIsLoading(true);
    setError(null);

    // Optimistic update
    setMessages(prev => [...prev, { role: 'user', content }]);

    try {
      const response = await chatApi.send(content, conversationId);

      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: response.message }
      ]);

      if (!conversationId) {
        setConversationId(response.conversation_id);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to send message';
      setError(message);
      // Remove optimistic message on error
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  }, [session, conversationId]);

  const loadConversation = useCallback(async (id: string) => {
    if (!session?.user) return;

    setIsLoading(true);
    setError(null);

    try {
      const conversation = await chatApi.getConversation(id);
      setMessages(conversation.messages || []);
      setConversationId(id);
    } catch (err) {
      setError('Failed to load conversation');
    } finally {
      setIsLoading(false);
    }
  }, [session]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  }, []);

  return {
    messages,
    conversationId,
    isLoading,
    error,
    isAuthenticated: !!session?.user,
    sendMessage,
    loadConversation,
    clearChat,
  };
}
```

## Protected Page Component

```tsx
// frontend/src/app/chat/page.tsx
'use client';

import { useSession } from '@/lib/auth-client';
import { ChatWindow } from '@/components/chat/ChatWindow';
import { redirect } from 'next/navigation';
import { useEffect } from 'react';

export default function ChatPage() {
  const { data: session, isPending } = useSession();

  useEffect(() => {
    if (!isPending && !session?.user) {
      redirect('/login');
    }
  }, [session, isPending]);

  if (isPending) {
    return (
      <div className="flex justify-center items-center h-screen">
        <span>Loading...</span>
      </div>
    );
  }

  if (!session?.user) {
    return null; // Will redirect
  }

  return (
    <main className="container mx-auto py-8 px-4">
      <h1 className="text-2xl font-bold mb-6">
        Welcome, {session.user.name || 'User'}
      </h1>
      <ChatWindow />
    </main>
  );
}
```

## Auth Context Provider

```tsx
// frontend/src/contexts/AuthContext.tsx
'use client';

import { createContext, useContext, ReactNode } from 'react';
import { useSession, signOut } from '@/lib/auth-client';

interface AuthContextType {
  user: { id: string; email: string; name?: string } | null;
  isLoading: boolean;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const { data: session, isPending } = useSession();

  const logout = async () => {
    await signOut();
  };

  return (
    <AuthContext.Provider
      value={{
        user: session?.user || null,
        isLoading: isPending,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

## Token Storage Strategy

Better Auth manages session cookies automatically. For API calls:

1. **Session Verification**: Check `useSession()` for user state
2. **Token Request**: Call `/api/auth/token` to get JWT
3. **API Calls**: Attach JWT in Authorization header
4. **Token Refresh**: Re-request token if 401 received

No manual token storage needed - Better Auth handles session persistence.
