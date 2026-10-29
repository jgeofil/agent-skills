# Zustand State Builder - Implementation Guide & Code Recipes

## Middleware

### DevTools Integration

```typescript
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface StoreState {
  count: number;
  increment: () => void;
}

export const useStore = create<StoreState>()(
  devtools(
    (set) => ({
      count: 0,
      increment: () =>
        set(
          (state) => ({ count: state.count + 1 }),
          false,
          'increment' // Action name for devtools
        ),
    }),
    { name: 'CounterStore' } // Store name in devtools
  )
);
```

### Persistence

```typescript
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

interface SettingsState {
  theme: 'light' | 'dark';
  language: string;
  notifications: boolean;
  setTheme: (theme: 'light' | 'dark') => void;
  setLanguage: (language: string) => void;
  toggleNotifications: () => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      theme: 'light',
      language: 'en',
      notifications: true,
      setTheme: (theme) => set({ theme }),
      setLanguage: (language) => set({ language }),
      toggleNotifications: () =>
        set((state) => ({ notifications: !state.notifications })),
    }),
    {
      name: 'settings-storage', // localStorage key
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        // Only persist these fields
        theme: state.theme,
        language: state.language,
        notifications: state.notifications,
      }),
    }
  )
);
```

### Immer Middleware

```typescript
import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';

interface Todo {
  id: string;
  text: string;
  completed: boolean;
}

interface TodosState {
  todos: Todo[];
  addTodo: (text: string) => void;
  toggleTodo: (id: string) => void;
  updateTodo: (id: string, text: string) => void;
  deleteTodo: (id: string) => void;
}

export const useTodosStore = create<TodosState>()(
  immer((set) => ({
    todos: [],

    addTodo: (text) =>
      set((state) => {
        state.todos.push({
          id: crypto.randomUUID(),
          text,
          completed: false,
        });
      }),

    toggleTodo: (id) =>
      set((state) => {
        const todo = state.todos.find((t) => t.id === id);
        if (todo) {
          todo.completed = !todo.completed;
        }
      }),

    updateTodo: (id, text) =>
      set((state) => {
        const todo = state.todos.find((t) => t.id === id);
        if (todo) {
          todo.text = text;
        }
      }),

    deleteTodo: (id) =>
      set((state) => {
        const index = state.todos.findIndex((t) => t.id === id);
        if (index !== -1) {
          state.todos.splice(index, 1);
        }
      }),
  }))
);
```

### Combined Middleware

```typescript
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

export const useStore = create<StoreState>()(
  devtools(
    persist(
      immer((set) => ({
        // ... state and actions
      })),
      { name: 'store' }
    ),
    { name: 'MyStore' }
  )
);
```

## Slices Pattern

### Modular Store Architecture

```typescript
// stores/slices/authSlice.ts
import { StateCreator } from 'zustand';

export interface AuthSlice {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

export const createAuthSlice: StateCreator<
  AuthSlice & CartSlice, // Combined state type
  [],
  [],
  AuthSlice
> = (set) => ({
  user: null,
  isAuthenticated: false,

  login: async (email, password) => {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    const user = await response.json();
    set({ user, isAuthenticated: true });
  },

  logout: () => set({ user: null, isAuthenticated: false }),
});
```

```typescript
// stores/slices/cartSlice.ts
import { StateCreator } from 'zustand';

interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
}

export interface CartSlice {
  items: CartItem[];
  addItem: (item: Omit<CartItem, 'quantity'>) => void;
  removeItem: (id: string) => void;
  updateQuantity: (id: string, quantity: number) => void;
  clearCart: () => void;
  totalItems: () => number;
  totalPrice: () => number;
}

export const createCartSlice: StateCreator<
  AuthSlice & CartSlice,
  [],
  [],
  CartSlice
> = (set, get) => ({
  items: [],

  addItem: (item) =>
    set((state) => {
      const existing = state.items.find((i) => i.id === item.id);
      if (existing) {
        return {
          items: state.items.map((i) =>
            i.id === item.id ? { ...i, quantity: i.quantity + 1 } : i
          ),
        };
      }
      return { items: [...state.items, { ...item, quantity: 1 }] };
    }),

  removeItem: (id) =>
    set((state) => ({
      items: state.items.filter((i) => i.id !== id),
    })),

  updateQuantity: (id, quantity) =>
    set((state) => ({
      items:
        quantity <= 0
          ? state.items.filter((i) => i.id !== id)
          : state.items.map((i) => (i.id === id ? { ...i, quantity } : i)),
    })),

  clearCart: () => set({ items: [] }),

  totalItems: () => get().items.reduce((sum, i) => sum + i.quantity, 0),

  totalPrice: () =>
    get().items.reduce((sum, i) => sum + i.price * i.quantity, 0),
});
```

```typescript
// stores/index.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { createAuthSlice, AuthSlice } from './slices/authSlice';
import { createCartSlice, CartSlice } from './slices/cartSlice';

type StoreState = AuthSlice & CartSlice;

export const useStore = create<StoreState>()(
  devtools(
    persist(
      (...args) => ({
        ...createAuthSlice(...args),
        ...createCartSlice(...args),
      }),
      {
        name: 'app-store',
        partialize: (state) => ({
          items: state.items, // Persist cart
          // Don't persist auth (handle with tokens)
        }),
      }
    ),
    { name: 'AppStore' }
  )
);
```

## Selectors

### Optimized Selectors

```typescript
// Avoid re-renders with selectors
function UserName() {
  // Only re-renders when user.name changes
  const userName = useStore((state) => state.user?.name);
  return <span>{userName}</span>;
}

// Multiple values with shallow comparison
import { shallow } from 'zustand/shallow';

function UserInfo() {
  const { name, email } = useStore(
    (state) => ({ name: state.user?.name, email: state.user?.email }),
    shallow
  );
  return (
    <div>
      <p>{name}</p>
      <p>{email}</p>
    </div>
  );
}

// Computed values
function CartSummary() {
  const totalItems = useStore((state) =>
    state.items.reduce((sum, i) => sum + i.quantity, 0)
  );
  const totalPrice = useStore((state) =>
    state.items.reduce((sum, i) => sum + i.price * i.quantity, 0)
  );

  return (
    <div>
      <p>Items: {totalItems}</p>
      <p>Total: ${totalPrice.toFixed(2)}</p>
    </div>
  );
}
```

### Reusable Selector Hooks

```typescript
// stores/selectors.ts
import { useStore } from './index';
import { shallow } from 'zustand/shallow';

// Auth selectors
export const useAuth = () =>
  useStore(
    (state) => ({
      user: state.user,
      isAuthenticated: state.isAuthenticated,
      login: state.login,
      logout: state.logout,
    }),
    shallow
  );

export const useUser = () => useStore((state) => state.user);
export const useIsAuthenticated = () => useStore((state) => state.isAuthenticated);

// Cart selectors
export const useCart = () =>
  useStore(
    (state) => ({
      items: state.items,
      addItem: state.addItem,
      removeItem: state.removeItem,
      updateQuantity: state.updateQuantity,
      clearCart: state.clearCart,
    }),
    shallow
  );

export const useCartTotal = () =>
  useStore((state) => ({
    items: state.items.reduce((sum, i) => sum + i.quantity, 0),
    price: state.items.reduce((sum, i) => sum + i.price * i.quantity, 0),
  }), shallow);
```

## Outside React Usage

```typescript
// Access store outside React components
const { getState, setState, subscribe } = useStore;

// Get current state
const currentUser = useStore.getState().user;

// Update state
useStore.setState({ user: newUser });

// Subscribe to changes
const unsubscribe = useStore.subscribe((state) => {
  console.log('State changed:', state);
});

// Subscribe to specific slice
const unsubscribeCart = useStore.subscribe(
  (state) => state.items,
  (items, previousItems) => {
    console.log('Cart changed:', items);
  }
);
```

## Server State Integration

### With TanStack Query

```typescript
// stores/ui.ts - Client state only
import { create } from 'zustand';

interface UIState {
  sidebarOpen: boolean;
  modalOpen: boolean;
  toggleSidebar: () => void;
  openModal: () => void;
  closeModal: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  modalOpen: false,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  openModal: () => set({ modalOpen: true }),
  closeModal: () => set({ modalOpen: false }),
}));

// hooks/useUsers.ts - Server state with TanStack Query
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: () => fetch('/api/users').then((r) => r.json()),
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (user: CreateUserDto) =>
      fetch('/api/users', {
        method: 'POST',
        body: JSON.stringify(user),
      }).then((r) => r.json()),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}
```

## Testing

```typescript
// stores/__tests__/counter.test.ts
import { act, renderHook } from '@testing-library/react';
import { useCounterStore } from '../counter';

describe('Counter Store', () => {
  beforeEach(() => {
    // Reset store before each test
    useCounterStore.setState({ count: 0 });
  });

  it('increments count', () => {
    const { result } = renderHook(() => useCounterStore());

    act(() => {
      result.current.increment();
    });

    expect(result.current.count).toBe(1);
  });

  it('decrements count', () => {
    useCounterStore.setState({ count: 5 });
    const { result } = renderHook(() => useCounterStore());

    act(() => {
      result.current.decrement();
    });

    expect(result.current.count).toBe(4);
  });

  it('resets count', () => {
    useCounterStore.setState({ count: 10 });
    const { result } = renderHook(() => useCounterStore());

    act(() => {
      result.current.reset();
    });

    expect(result.current.count).toBe(0);
  });
});
```
