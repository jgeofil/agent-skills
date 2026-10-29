---
name: react-hook-builder
description: >-
  Creates custom React hooks for common patterns including data fetching, forms, authentication, local storage, debounce, and more. Use when users request "create custom hook", "React hook for", "useX hook", or "reusable hook".
license: MIT
metadata:
  version: "1.0"
  category: frontend-swe
---

# React Hook Builder

Build production-ready custom React hooks following best practices and TypeScript patterns.

## Core Workflow

1. **Identify the pattern**: Determine what logic to encapsulate
2. **Design the API**: Define inputs, outputs, and options
3. **Add TypeScript types**: Full type safety with generics
4. **Handle edge cases**: Loading, errors, cleanup
5. **Optimize performance**: Memoization where needed
6. **Write tests**: Cover all states and scenarios

## Hook Naming Conventions

```typescript
// Always prefix with "use"
useLocalStorage     // ✓
useDebounce         // ✓
useFetch            // ✓
localStorageHook    // ✗
fetchData           // ✗
```

## Data Fetching Hooks

### useFetch

```typescript
// hooks/useFetch.ts
import { useState, useEffect, useCallback, useRef } from 'react';

interface UseFetchOptions<T> {
  immediate?: boolean;
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
}

interface UseFetchResult<T> {
  data: T | null;
  error: Error | null;
  isLoading: boolean;
  isError: boolean;
  isSuccess: boolean;
  refetch: () => Promise<void>;
}

export function useFetch<T>(
  url: string | null,
  options: UseFetchOptions<T> = {}
): UseFetchResult<T> {
  const { immediate = true, onSuccess, onError } = options;

  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const abortControllerRef = useRef<AbortController | null>(null);

  const fetchData = useCallback(async () => {
    if (!url) return;

    // Cancel previous request
    abortControllerRef.current?.abort();
    abortControllerRef.current = new AbortController();

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(url, {
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setData(result);
      onSuccess?.(result);
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        return; // Ignore abort errors
      }
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      onError?.(error);
    } finally {
      setIsLoading(false);
    }
  }, [url, onSuccess, onError]);

  useEffect(() => {
    if (immediate) {
      fetchData();
    }

    return () => {
      abortControllerRef.current?.abort();
    };
  }, [fetchData, immediate]);

  return {
    data,
    error,
    isLoading,
    isError: !!error,
    isSuccess: !!data && !error,
    refetch: fetchData,
  };
}

// Usage
function UserProfile({ userId }: { userId: string }) {
  const { data: user, isLoading, error } = useFetch<User>(
    `/api/users/${userId}`
  );

  if (isLoading) return <Spinner />;
  if (error) return <Error message={error.message} />;
  return <Profile user={user!} />;
}
```

### useMutation

```typescript
// hooks/useMutation.ts
import { useState, useCallback } from 'react';

interface UseMutationOptions<TData, TVariables> {
  onSuccess?: (data: TData, variables: TVariables) => void;
  onError?: (error: Error, variables: TVariables) => void;
  onSettled?: (data: TData | undefined, error: Error | null, variables: TVariables) => void;
}

interface UseMutationResult<TData, TVariables> {
  data: TData | null;
  error: Error | null;
  isLoading: boolean;
  isError: boolean;
  isSuccess: boolean;
  mutate: (variables: TVariables) => Promise<TData | undefined>;
  reset: () => void;
}

export function useMutation<TData, TVariables>(
  mutationFn: (variables: TVariables) => Promise<TData>,
  options: UseMutationOptions<TData, TVariables> = {}
): UseMutationResult<TData, TVariables> {
  const { onSuccess, onError, onSettled } = options;

  const [data, setData] = useState<TData | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const mutate = useCallback(
    async (variables: TVariables) => {
      setIsLoading(true);
      setError(null);

      try {
        const result = await mutationFn(variables);
        setData(result);
        onSuccess?.(result, variables);
        onSettled?.(result, null, variables);
        return result;
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Unknown error');
        setError(error);
        onError?.(error, variables);
        onSettled?.(undefined, error, variables);
        return undefined;
      } finally {
        setIsLoading(false);
      }
    },
    [mutationFn, onSuccess, onError, onSettled]
  );

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setIsLoading(false);
  }, []);

  return {
    data,
    error,
    isLoading,
    isError: !!error,
    isSuccess: !!data && !error,
    mutate,
    reset,
  };
}

// Usage
function CreateUser() {
  const { mutate, isLoading } = useMutation(
    async (data: CreateUserDto) => {
      const res = await fetch('/api/users', {
        method: 'POST',
        body: JSON.stringify(data),
      });
      return res.json();
    },
    {
      onSuccess: () => toast.success('User created!'),
    }
  );

  return (
    <button onClick={() => mutate({ name: 'John' })} disabled={isLoading}>
      Create User
    </button>
  );
}
```

## Best Practices

1. **Start with `use`**: All hooks must start with `use`
2. **Single responsibility**: Each hook does one thing well
3. **Return consistent types**: Always return same shape
4. **Handle cleanup**: Use `useEffect` cleanup for subscriptions
5. **Memoize callbacks**: Use `useCallback` for stable references
6. **Type everything**: Full TypeScript types with generics
7. **Document API**: JSDoc comments for parameters
8. **Test all states**: Loading, error, success, edge cases

## Output Checklist

Every custom hook should include:

- [ ] Hook name starts with `use`
- [ ] Full TypeScript types for inputs and outputs
- [ ] Proper cleanup in useEffect
- [ ] Stable callback references with useCallback
- [ ] Error handling for edge cases
- [ ] SSR safety (check for `window`)
- [ ] Unit tests covering all states
- [ ] JSDoc documentation
- [ ] Usage example in comments


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

