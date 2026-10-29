---
name: react-server-components
description: >-
  Implements React Server Components (RSC) patterns with Next.js App Router including data fetching, streaming, selective hydration, and server/client composition. Use when users request "server components", "RSC", "Next.js app router", "server-side rendering", or "streaming".
license: MIT
metadata:
  version: "1.0"
  category: frontend-swe
---

# React Server Components

Build performant applications with React Server Components and Next.js App Router.

## Core Workflow

1. **Understand RSC model**: Server vs client components
2. **Design component tree**: Plan server/client boundaries
3. **Implement data fetching**: Fetch in server components
4. **Add interactivity**: Client components where needed
5. **Enable streaming**: Suspense for progressive loading
6. **Optimize**: Minimize client bundle size

## Server vs Client Components

### Key Differences

| Feature | Server Components | Client Components |
|---------|-------------------|-------------------|
| Rendering | Server only | Server + Client |
| Bundle size | Zero JS sent | Adds to bundle |
| Data fetching | Direct DB/API access | useEffect/TanStack Query |
| State/Effects | No hooks | Full React hooks |
| Event handlers | No | Yes |
| Browser APIs | No | Yes |
| File directive | Default (none) | `'use client'` |

### When to Use Each

**Server Components (Default)**
- Static content
- Data fetching
- Backend resource access
- Large dependencies (markdown, syntax highlighting)
- Sensitive logic/tokens

**Client Components**
- Interactive UI (onClick, onChange)
- useState, useEffect, useReducer
- Browser APIs (localStorage, geolocation)
- Custom hooks with state
- Third-party client libraries

## Basic Patterns

### Server Component (Default)

```tsx
// app/users/page.tsx (Server Component - no directive needed)
import { db } from '@/lib/db';

async function getUsers() {
  return db.user.findMany({
    orderBy: { createdAt: 'desc' },
  });
}

export default async function UsersPage() {
  const users = await getUsers();

  return (
    <div>
      <h1>Users</h1>
      <ul>
        {users.map((user) => (
          <li key={user.id}>{user.name}</li>
        ))}
      </ul>
    </div>
  );
}
```

### Client Component

```tsx
// components/Counter.tsx
'use client';

import { useState } from 'react';

export function Counter() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount(count + 1)}>
      Count: {count}
    </button>
  );
}
```

### Composition Pattern

```tsx
// app/dashboard/page.tsx (Server Component)
import { db } from '@/lib/db';
import { DashboardClient } from './DashboardClient';
import { StatsCard } from '@/components/StatsCard';

async function getStats() {
  const [users, orders, revenue] = await Promise.all([
    db.user.count(),
    db.order.count(),
    db.order.aggregate({ _sum: { total: true } }),
  ]);
  return { users, orders, revenue: revenue._sum.total };
}

export default async function DashboardPage() {
  const stats = await getStats();

  return (
    <div>
      {/* Server-rendered static content */}
      <h1>Dashboard</h1>

      {/* Server components with data */}
      <div className="grid grid-cols-3 gap-4">
        <StatsCard title="Users" value={stats.users} />
        <StatsCard title="Orders" value={stats.orders} />
        <StatsCard title="Revenue" value={`$${stats.revenue}`} />
      </div>

      {/* Client component for interactivity */}
      <DashboardClient initialData={stats} />
    </div>
  );
}
```

```tsx
// app/dashboard/DashboardClient.tsx
'use client';

import { useState } from 'react';
import { DateRangePicker } from '@/components/DateRangePicker';
import { Chart } from '@/components/Chart';

interface DashboardClientProps {
  initialData: Stats;
}

export function DashboardClient({ initialData }: DashboardClientProps) {
  const [dateRange, setDateRange] = useState({ from: null, to: null });

  return (
    <div>
      <DateRangePicker value={dateRange} onChange={setDateRange} />
      <Chart data={initialData} />
    </div>
  );
}
```

## Best Practices

1. **Start with Server Components**: Default to server, add 'use client' only when needed
2. **Push client boundaries down**: Keep interactivity in leaf components
3. **Parallel fetch data**: Use Promise.all for independent data
4. **Use Suspense for streaming**: Progressive loading for better UX
5. **Colocate data fetching**: Fetch where data is used
6. **Minimize client bundle**: Heavy libraries stay on server
7. **Cache appropriately**: Use revalidation strategies
8. **Handle errors**: Use error.tsx boundaries

## Output Checklist

Every RSC implementation should include:

- [ ] Server components for data fetching
- [ ] 'use client' only where needed
- [ ] Suspense boundaries for streaming
- [ ] Loading skeletons for each section
- [ ] Parallel data fetching with Promise.all
- [ ] Server actions for mutations
- [ ] Proper caching strategy
- [ ] Error boundaries (error.tsx)
- [ ] Authentication checks in layouts
- [ ] Minimal client JavaScript bundle


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

