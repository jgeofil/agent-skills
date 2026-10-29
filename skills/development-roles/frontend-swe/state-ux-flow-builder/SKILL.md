---
name: state-ux-flow-builder
description: >-
  Standardizes UX states for data fetching flows (loading skeletons, error boundaries with retry, empty states with CTAs, success states) and complex multi-view UI patterns. Provides state machine recommendations and optimistic update patterns. Use when implementing "loading states", "error handling", "empty states", or "state machines".
license: MIT
metadata:
  version: "1.0"
  category: frontend-swe
---

# State & UX Flow Builder

Standardize and implement bulletproof user experience flows across all asynchronous states: loading, error, empty, and success.

## When to Use This Skill

- Designing data fetching workflows in React, Vue, or Svelte applications
- Implementing accessible skeleton loaders, error boundaries, and empty state fallbacks
- Managing multi-step flows and complex UI transitions with deterministic state machines
- Adding optimistic UI updates with automatic rollback on network failure

## The Complete UX State Matrix

Every asynchronous UI component must explicitly handle these five states:

| State | Component Pattern | User Experience Requirement |
|---|---|---|
| **Idle / Initial** | Placeholder or neutral shell | Immediate layout stability, prevent layout shift (CLS). |
| **Loading** | Accessible Skeleton Loader | Mirror target layout; pulse animation; no blocking spinners. |
| **Error** | Error Alert + Retry CTA | Clear user-friendly copy; action to retry; logs to monitoring. |
| **Empty** | Zero-Data Graphic + Action | Explain why data is absent; clear CTA to create or reset filters. |
| **Success** | Data Presentation | Smooth transition; preserve scroll position and focus. |

## Core Implementation Pattern

```tsx
interface DataStateWrapperProps<T> {
  isLoading: boolean;
  error: Error | null;
  data: T[] | null | undefined;
  onRetry: () => void;
  skeleton: React.ReactNode;
  emptyCTA: React.ReactNode;
  children: (data: T[]) => React.ReactNode;
}

export function DataStateWrapper<T>({
  isLoading,
  error,
  data,
  onRetry,
  skeleton,
  emptyCTA,
  children,
}: DataStateWrapperProps<T>) {
  if (isLoading) return <>{skeleton}</>;
  
  if (error) {
    return (
      <div role="alert" className="p-6 rounded-lg bg-red-50 text-red-800 border border-red-200">
        <p className="font-medium">Failed to load information</p>
        <p className="text-sm text-red-600 mt-1">{error.message}</p>
        <button 
          onClick={onRetry} 
          className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm font-medium"
        >
          Try Again
        </button>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return <>{emptyCTA}</>;
  }

  return <>{children(data)}</>;
}
```

## Best Practices

1. **Prevent Layout Shifts**: Skeletons must match the exact dimensions of final content.
2. **Accessible Live Regions**: Mark loading state changes with `aria-busy="true"` and error containers with `role="alert"`.
3. **Optimistic Updates**: Update local client state immediately; maintain previous snapshot for rollback if mutation rejects.
4. **Error Boundaries**: Wrap major UI sections in React Error Boundaries to prevent full-page crashes.
