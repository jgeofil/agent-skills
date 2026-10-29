---
name: websocket-realtime-builder
description: >-
  Implements real-time features using WebSockets with Socket.io, rooms, authentication, and reconnection handling. Use when users request "real-time updates", "WebSocket", "Socket.io", "live chat", or "push notifications".
license: MIT
metadata:
  version: "1.0"
  category: backend-swe
---

# WebSocket Realtime Builder

Build real-time applications with WebSockets and Socket.io.

## Core Workflow

1. **Choose library**: Socket.io vs native WebSocket
2. **Setup server**: Configure WebSocket server
3. **Add authentication**: Validate connections
4. **Implement rooms**: Group connections
5. **Handle events**: Define event handlers
6. **Add reconnection**: Handle disconnects gracefully

## Installation

```bash
# Server
npm install socket.io

# Client
npm install socket.io-client
```

## Server Setup

### Basic Socket.io Server

```typescript
// server.ts
import express from 'express';
import { createServer } from 'http';
import { Server, Socket } from 'socket.io';
import { verifyToken } from './auth';

const app = express();
const httpServer = createServer(app);

const io = new Server(httpServer, {
  cors: {
    origin: process.env.CLIENT_URL,
    credentials: true,
  },
  pingInterval: 25000,
  pingTimeout: 60000,
});

// Authentication middleware
io.use(async (socket, next) => {
  const token = socket.handshake.auth.token;

  if (!token) {
    return next(new Error('Authentication required'));
  }

  try {
    const user = await verifyToken(token);
    socket.data.user = user;
    next();
  } catch (err) {
    next(new Error('Invalid token'));
  }
});

io.on('connection', (socket: Socket) => {
  const user = socket.data.user;
  console.log(`User connected: ${user.id}`);

  // Join user's personal room
  socket.join(`user:${user.id}`);

  // Handle events
  socket.on('disconnect', () => {
    console.log(`User disconnected: ${user.id}`);
  });
});

httpServer.listen(3001, () => {
  console.log('Socket.io server running on port 3001');
});

export { io };
```

### Namespaces and Rooms

```typescript
// namespaces/chat.ts
import { Server, Socket } from 'socket.io';

export function setupChatNamespace(io: Server) {
  const chatNamespace = io.of('/chat');

  chatNamespace.on('connection', (socket: Socket) => {
    const user = socket.data.user;

    // Join a chat room
    socket.on('join-room', async (roomId: string) => {
      // Validate user can access this room
      const canAccess = await canAccessRoom(user.id, roomId);
      if (!canAccess) {
        socket.emit('error', { message: 'Access denied' });
        return;
      }

      socket.join(`room:${roomId}`);
      socket.to(`room:${roomId}`).emit('user-joined', {
        userId: user.id,
        name: user.name,
      });
    });

    // Leave a chat room
    socket.on('leave-room', (roomId: string) => {
      socket.leave(`room:${roomId}`);
      socket.to(`room:${roomId}`).emit('user-left', {
        userId: user.id,
      });
    });

    // Send message
    socket.on('send-message', async (data: { roomId: string; content: string }) => {
      const { roomId, content } = data;

      // Save to database
      const message = await db.message.create({
        data: {
          roomId,
          authorId: user.id,
          content,
        },
        include: { author: true },
      });

      // Broadcast to room
      chatNamespace.to(`room:${roomId}`).emit('new-message', {
        id: message.id,
        content: message.content,
        author: {
          id: user.id,
          name: user.name,
        },
        createdAt: message.createdAt,
      });
    });

    // Typing indicator
    socket.on('typing-start', (roomId: string) => {
      socket.to(`room:${roomId}`).emit('user-typing', {
        userId: user.id,
        name: user.name,
      });
    });

    socket.on('typing-stop', (roomId: string) => {
      socket.to(`room:${roomId}`).emit('user-stopped-typing', {
        userId: user.id,
      });
    });
  });

  return chatNamespace;
}
```

### Event Emitters

```typescript
// services/notifications.ts
import { io } from '../server';

export class NotificationService {
  // Send to specific user
  static sendToUser(userId: string, event: string, data: any) {
    io.to(`user:${userId}`).emit(event, data);
  }

  // Send to multiple users
  static sendToUsers(userIds: string[], event: string, data: any) {
    userIds.forEach((userId) => {
      io.to(`user:${userId}`).emit(event, data);
    });
  }

  // Broadcast to all connected users
  static broadcast(event: string, data: any) {
    io.emit(event, data);
  }

  // Send to room
  static sendToRoom(roomId: string, event: string, data: any) {
    io.to(`room:${roomId}`).emit(event, data);
  }

  // Notify new order
  static notifyNewOrder(order: Order) {
    // Notify customer
    this.sendToUser(order.customerId, 'order:created', {
      orderId: order.id,
      status: order.status,
    });

    // Notify admins
    io.to('role:admin').emit('admin:new-order', {
      orderId: order.id,
      customer: order.customerName,
      total: order.total,
    });
  }
}
```

## Best Practices

1. **Authenticate connections**: Validate tokens on connect
2. **Use rooms**: Group users logically
3. **Handle reconnection**: Re-sync state after reconnect
4. **Debounce events**: Prevent flooding (e.g., typing indicator)
5. **Clean up listeners**: Remove on component unmount
6. **Acknowledge important events**: Confirm critical messages
7. **Use namespaces**: Separate concerns (chat, notifications)
8. **Scale with Redis**: Use Redis adapter for multiple servers

## Output Checklist

Every WebSocket implementation should include:

- [ ] Server with authentication middleware
- [ ] Client hook with reconnection handling
- [ ] Room/namespace organization
- [ ] Event type definitions
- [ ] Error handling and recovery
- [ ] Typing indicators for chat
- [ ] Presence system (online/offline)
- [ ] Clean disconnect handling
- [ ] Rate limiting for events
- [ ] Redis adapter for scaling (production)


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

