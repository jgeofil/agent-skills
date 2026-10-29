# WebSocket Realtime Builder - Implementation Guide & Code Recipes

## Client Setup

### React Client Hook

```typescript
// hooks/useSocket.ts
import { useEffect, useRef, useState, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';
import { useAuth } from './useAuth';

interface UseSocketOptions {
  namespace?: string;
  autoConnect?: boolean;
}

export function useSocket(options: UseSocketOptions = {}) {
  const { namespace = '/', autoConnect = true } = options;
  const { token } = useAuth();
  const socketRef = useRef<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token || !autoConnect) return;

    const socket = io(`${process.env.NEXT_PUBLIC_WS_URL}${namespace}`, {
      auth: { token },
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
    });

    socket.on('connect', () => {
      setIsConnected(true);
      setError(null);
    });

    socket.on('disconnect', () => {
      setIsConnected(false);
    });

    socket.on('connect_error', (err) => {
      setError(err.message);
      setIsConnected(false);
    });

    socketRef.current = socket;

    return () => {
      socket.disconnect();
    };
  }, [token, namespace, autoConnect]);

  const emit = useCallback((event: string, data?: any) => {
    socketRef.current?.emit(event, data);
  }, []);

  const on = useCallback((event: string, handler: (...args: any[]) => void) => {
    socketRef.current?.on(event, handler);
    return () => {
      socketRef.current?.off(event, handler);
    };
  }, []);

  const off = useCallback((event: string, handler?: (...args: any[]) => void) => {
    socketRef.current?.off(event, handler);
  }, []);

  return {
    socket: socketRef.current,
    isConnected,
    error,
    emit,
    on,
    off,
  };
}
```

### Chat Hook

```typescript
// hooks/useChat.ts
import { useEffect, useState, useCallback } from 'react';
import { useSocket } from './useSocket';

interface Message {
  id: string;
  content: string;
  author: { id: string; name: string };
  createdAt: string;
}

interface TypingUser {
  userId: string;
  name: string;
}

export function useChat(roomId: string) {
  const { socket, isConnected, emit, on } = useSocket({ namespace: '/chat' });
  const [messages, setMessages] = useState<Message[]>([]);
  const [typingUsers, setTypingUsers] = useState<TypingUser[]>([]);

  // Join room on connect
  useEffect(() => {
    if (isConnected && roomId) {
      emit('join-room', roomId);

      return () => {
        emit('leave-room', roomId);
      };
    }
  }, [isConnected, roomId, emit]);

  // Listen for messages
  useEffect(() => {
    const unsubMessage = on('new-message', (message: Message) => {
      setMessages((prev) => [...prev, message]);
    });

    const unsubTyping = on('user-typing', (user: TypingUser) => {
      setTypingUsers((prev) => {
        if (prev.some((u) => u.userId === user.userId)) return prev;
        return [...prev, user];
      });
    });

    const unsubStopTyping = on('user-stopped-typing', ({ userId }: { userId: string }) => {
      setTypingUsers((prev) => prev.filter((u) => u.userId !== userId));
    });

    return () => {
      unsubMessage();
      unsubTyping();
      unsubStopTyping();
    };
  }, [on]);

  const sendMessage = useCallback((content: string) => {
    emit('send-message', { roomId, content });
  }, [emit, roomId]);

  const startTyping = useCallback(() => {
    emit('typing-start', roomId);
  }, [emit, roomId]);

  const stopTyping = useCallback(() => {
    emit('typing-stop', roomId);
  }, [emit, roomId]);

  return {
    messages,
    typingUsers,
    sendMessage,
    startTyping,
    stopTyping,
    isConnected,
  };
}
```

### Chat Component

```tsx
// components/ChatRoom.tsx
'use client';

import { useState, useRef, useEffect } from 'react';
import { useChat } from '@/hooks/useChat';

export function ChatRoom({ roomId }: { roomId: string }) {
  const {
    messages,
    typingUsers,
    sendMessage,
    startTyping,
    stopTyping,
    isConnected,
  } = useChat(roomId);

  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout>();

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value);

    // Debounced typing indicator
    startTyping();
    clearTimeout(typingTimeoutRef.current);
    typingTimeoutRef.current = setTimeout(stopTyping, 2000);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    sendMessage(input);
    setInput('');
    stopTyping();
  };

  if (!isConnected) {
    return <div>Connecting...</div>;
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div key={message.id} className="flex gap-2">
            <span className="font-semibold">{message.author.name}:</span>
            <span>{message.content}</span>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {typingUsers.length > 0 && (
        <div className="px-4 py-2 text-sm text-gray-500">
          {typingUsers.map((u) => u.name).join(', ')}{' '}
          {typingUsers.length === 1 ? 'is' : 'are'} typing...
        </div>
      )}

      <form onSubmit={handleSubmit} className="p-4 border-t">
        <input
          type="text"
          value={input}
          onChange={handleInputChange}
          placeholder="Type a message..."
          className="w-full px-4 py-2 border rounded"
        />
      </form>
    </div>
  );
}
```

## Real-time Notifications

```typescript
// hooks/useNotifications.ts
import { useEffect, useState } from 'react';
import { useSocket } from './useSocket';
import { toast } from 'sonner';

interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  createdAt: string;
  read: boolean;
}

export function useNotifications() {
  const { on, isConnected } = useSocket();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    const unsubscribe = on('notification', (notification: Notification) => {
      setNotifications((prev) => [notification, ...prev]);
      setUnreadCount((prev) => prev + 1);

      // Show toast
      toast(notification.title, {
        description: notification.message,
      });
    });

    return unsubscribe;
  }, [on]);

  const markAsRead = (id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
    setUnreadCount((prev) => Math.max(0, prev - 1));
  };

  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
    setUnreadCount(0);
  };

  return {
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
    isConnected,
  };
}
```

## Presence System

```typescript
// server/presence.ts
import { Server, Socket } from 'socket.io';

interface UserPresence {
  odlineserId: string;
  name: string;
  status: 'online' | 'away' | 'busy';
  lastSeen: Date;
}

const onlineUsers = new Map<string, UserPresence>();

export function setupPresence(io: Server) {
  io.on('connection', (socket: Socket) => {
    const user = socket.data.user;

    // User comes online
    onlineUsers.set(user.id, {
      odlineserId: user.id,
      name: user.name,
      status: 'online',
      lastSeen: new Date(),
    });

    // Broadcast to all users
    io.emit('presence:update', {
      userId: user.id,
      status: 'online',
    });

    // Send current online users to new connection
    socket.emit('presence:list', Array.from(onlineUsers.values()));

    // Handle status changes
    socket.on('presence:status', (status: 'online' | 'away' | 'busy') => {
      const presence = onlineUsers.get(user.id);
      if (presence) {
        presence.status = status;
        io.emit('presence:update', { userId: user.id, status });
      }
    });

    // Handle disconnect
    socket.on('disconnect', () => {
      onlineUsers.delete(user.id);
      io.emit('presence:update', {
        userId: user.id,
        status: 'offline',
      });
    });
  });
}
```

## Error Handling & Reconnection

```typescript
// Client-side error handling
const socket = io(WS_URL, {
  auth: { token },
  reconnection: true,
  reconnectionAttempts: 10,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 10000,
  timeout: 20000,
});

socket.on('connect_error', (error) => {
  if (error.message === 'Authentication required') {
    // Redirect to login
    router.push('/login');
  } else {
    console.error('Connection error:', error);
  }
});

socket.on('reconnect', (attemptNumber) => {
  console.log(`Reconnected after ${attemptNumber} attempts`);
  // Re-sync state
  socket.emit('sync-state');
});

socket.on('reconnect_failed', () => {
  console.error('Failed to reconnect');
  // Show user notification
  toast.error('Connection lost. Please refresh the page.');
});
```
