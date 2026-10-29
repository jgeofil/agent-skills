---
name: zustand-state-builder
description: >-
  Implements lightweight state management using Zustand with TypeScript, persistence, devtools, and modular store patterns. Use when users request "zustand store", "state management", "global state", "zustand setup", or "jotai alternative".
license: MIT
metadata:
  version: "1.0"
  category: frontend-swe
---

# Zustand State Builder

Build lightweight, scalable state management with Zustand's minimal API.

## Core Workflow

1. **Identify state needs**: Determine what needs global state
2. **Create store**: Define state shape and actions
3. **Add TypeScript types**: Full type safety
4. **Enable middleware**: Devtools, persist, immer
5. **Split stores**: Modular slices for large apps
6. **Connect components**: Use hooks to access state

## Installation

```bash
npm install zustand

# Optional middleware
npm install immer  # For immutable updates
```

## Basic Store

### Simple Counter Store

```typescript
// stores/counter.ts
import { create } from 'zustand';

interface CounterState {
  count: number;
  increment: () => void;
  decrement: () => void;
  reset: () => void;
  incrementBy: (amount: number) => void;
}

export const useCounterStore = create<CounterState>((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 })),
  reset: () => set({ count: 0 }),
  incrementBy: (amount) => set((state) => ({ count: state.count + amount })),
}));

// Usage in component
function Counter() {
  const { count, increment, decrement } = useCounterStore();

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={increment}>+</button>
      <button onClick={decrement}>-</button>
    </div>
  );
}
```

### Async Actions

```typescript
// stores/users.ts
import { create } from 'zustand';

interface User {
  id: string;
  name: string;
  email: string;
}

interface UsersState {
  users: User[];
  isLoading: boolean;
  error: string | null;
  fetchUsers: () => Promise<void>;
  addUser: (user: Omit<User, 'id'>) => Promise<void>;
  deleteUser: (id: string) => Promise<void>;
}

export const useUsersStore = create<UsersState>((set, get) => ({
  users: [],
  isLoading: false,
  error: null,

  fetchUsers: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch('/api/users');
      const users = await response.json();
      set({ users, isLoading: false });
    } catch (error) {
      set({ error: 'Failed to fetch users', isLoading: false });
    }
  },

  addUser: async (userData) => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch('/api/users', {
        method: 'POST',
        body: JSON.stringify(userData),
      });
      const newUser = await response.json();
      set((state) => ({
        users: [...state.users, newUser],
        isLoading: false,
      }));
    } catch (error) {
      set({ error: 'Failed to add user', isLoading: false });
    }
  },

  deleteUser: async (id) => {
    const previousUsers = get().users;
    // Optimistic update
    set((state) => ({
      users: state.users.filter((u) => u.id !== id),
    }));
    try {
      await fetch(`/api/users/${id}`, { method: 'DELETE' });
    } catch (error) {
      // Rollback on error
      set({ users: previousUsers, error: 'Failed to delete user' });
    }
  },
}));
```

## Best Practices

1. **Keep stores small**: One store per domain
2. **Use selectors**: Prevent unnecessary re-renders
3. **Separate client/server state**: Use TanStack Query for server state
4. **Enable devtools**: Essential for debugging
5. **Type everything**: Full TypeScript coverage
6. **Use immer for nested state**: Cleaner immutable updates
7. **Persist sparingly**: Only persist what's needed
8. **Test stores**: Unit test actions and state changes

## Output Checklist

Every Zustand store should include:

- [ ] TypeScript interfaces for state and actions
- [ ] Devtools middleware enabled
- [ ] Persistence where needed
- [ ] Selectors for optimized re-renders
- [ ] Slices pattern for large stores
- [ ] Async action error handling
- [ ] Outside React access method
- [ ] Unit tests for actions
- [ ] Integration with server state library


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

