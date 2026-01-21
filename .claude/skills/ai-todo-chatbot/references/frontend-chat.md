# Frontend Chat Implementation

## Chat API Client

```typescript
// frontend/src/lib/chat-api.ts
import { getAuthToken } from '@/lib/auth';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
  messages: ChatMessage[];
}

export const chatApi = {
  async send(message: string, conversationId?: string | null): Promise<ChatResponse> {
    const token = await getAuthToken();
    const response = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    return response.json();
  },

  async getConversations(): Promise<{ conversations: Conversation[] }> {
    const token = await getAuthToken();
    const response = await fetch(`${API_BASE}/api/chat/conversations`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to get conversations');
    }

    return response.json();
  },

  async getConversation(id: string): Promise<Conversation> {
    const token = await getAuthToken();
    const response = await fetch(`${API_BASE}/api/chat/conversations/${id}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to get conversation');
    }

    return response.json();
  },

  async deleteConversation(id: string): Promise<void> {
    const token = await getAuthToken();
    const response = await fetch(`${API_BASE}/api/chat/conversations/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to delete conversation');
    }
  },
};
```

## useChat Hook

```typescript
// frontend/src/hooks/useChat.ts
import { useState, useCallback } from 'react';
import { chatApi, ChatMessage } from '@/lib/chat-api';

export function useChat(initialConversationId?: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(
    initialConversationId || null
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    setIsLoading(true);
    setError(null);

    // Optimistically add user message
    setMessages(prev => [...prev, { role: 'user', content }]);

    try {
      const response = await chatApi.send(content, conversationId);

      // Add assistant response
      setMessages(prev => [...prev, { role: 'assistant', content: response.message }]);

      // Update conversation ID for subsequent messages
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }
    } catch (err) {
      setError('Failed to send message. Please try again.');
      // Remove the optimistically added user message
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  }, [conversationId]);

  const loadConversation = useCallback(async (id: string) => {
    setIsLoading(true);
    try {
      const conversation = await chatApi.getConversation(id);
      setMessages(conversation.messages);
      setConversationId(id);
    } catch (err) {
      setError('Failed to load conversation');
    } finally {
      setIsLoading(false);
    }
  }, []);

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
    sendMessage,
    loadConversation,
    clearChat,
  };
}
```

## Chat Components

### MessageBubble

```tsx
// frontend/src/components/chat/MessageBubble.tsx
interface MessageBubbleProps {
  role: 'user' | 'assistant';
  content: string;
}

export function MessageBubble({ role, content }: MessageBubbleProps) {
  const isUser = role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
        }`}
      >
        <p className="whitespace-pre-wrap">{content}</p>
      </div>
    </div>
  );
}
```

### ChatInput

```tsx
// frontend/src/components/chat/ChatInput.tsx
import { useState, FormEvent, KeyboardEvent } from 'react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({
  onSend,
  disabled = false,
  placeholder = 'Type a message...',
}: ChatInputProps) {
  const [input, setInput] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 p-4 border-t">
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        rows={1}
        className="flex-1 resize-none rounded-lg border px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={disabled || !input.trim()}
        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Send
      </button>
    </form>
  );
}
```

### ChatWindow

```tsx
// frontend/src/components/chat/ChatWindow.tsx
import { useRef, useEffect } from 'react';
import { MessageBubble } from './MessageBubble';
import { ChatInput } from './ChatInput';
import { useChat } from '@/hooks/useChat';

export function ChatWindow() {
  const { messages, isLoading, error, sendMessage } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-[600px] max-w-2xl mx-auto border rounded-lg">
      {/* Header */}
      <div className="px-4 py-3 border-b bg-gray-50 dark:bg-gray-900">
        <h2 className="font-semibold">Task Assistant</h2>
        <p className="text-sm text-gray-500">Manage your tasks with natural language</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <p>Start a conversation!</p>
            <p className="text-sm mt-2">Try: "Add a task to buy groceries"</p>
          </div>
        )}

        {messages.map((msg, index) => (
          <MessageBubble key={index} role={msg.role} content={msg.content} />
        ))}

        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-100 dark:bg-gray-800 rounded-lg px-4 py-2">
              <span className="animate-pulse">Thinking...</span>
            </div>
          </div>
        )}

        {error && (
          <div className="text-center text-red-500 mb-4">{error}</div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput onSend={sendMessage} disabled={isLoading} />
    </div>
  );
}
```

### Chat Page

```tsx
// frontend/src/app/chat/page.tsx
'use client';

import { useAuth } from '@/contexts/AuthContext';
import { ChatWindow } from '@/components/chat/ChatWindow';
import { redirect } from 'next/navigation';

export default function ChatPage() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }

  if (!user) {
    redirect('/login');
  }

  return (
    <main className="container mx-auto py-8 px-4">
      <h1 className="text-2xl font-bold mb-6">Task Chat</h1>
      <ChatWindow />
    </main>
  );
}
```
