# Page Layout Builder - Implementation Guide & Code Recipes

## Navigation Components

### Sidebar Navigation

```typescript
// components/Sidebar.tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  HomeIcon,
  UsersIcon,
  SettingsIcon,
  ChartBarIcon,
} from "@/components/icons";

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: HomeIcon },
  { name: "Users", href: "/users", icon: UsersIcon },
  { name: "Analytics", href: "/analytics", icon: ChartBarIcon },
  { name: "Settings", href: "/settings", icon: SettingsIcon },
];

export function Sidebar({ className }: { className?: string }) {
  const pathname = usePathname();

  return (
    <aside className={cn("border-r bg-white", className)}>
      <div className="flex h-16 items-center px-6">
        <span className="text-xl font-bold">AppName</span>
      </div>

      <nav className="space-y-1 px-3">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary-50 text-primary-600"
                  : "text-gray-700 hover:bg-gray-100"
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
```

### Header with User Menu

```typescript
// components/Header.tsx
"use client";

import { Button } from "@/components/ui/button";
import { Avatar } from "@/components/ui/avatar";
import { DropdownMenu } from "@/components/ui/dropdown-menu";
import { BellIcon, MenuIcon } from "@/components/icons";

export function Header() {
  return (
    <header className="flex h-16 items-center justify-between border-b bg-white px-4 md:px-6">
      {/* Mobile menu button */}
      <Button variant="ghost" size="icon" className="lg:hidden">
        <MenuIcon className="h-6 w-6" />
      </Button>

      {/* Search (optional) */}
      <div className="flex-1 px-4">{/* Search component */}</div>

      {/* Right side actions */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon">
          <BellIcon className="h-5 w-5" />
        </Button>

        <DropdownMenu>
          <Avatar src="/avatar.jpg" alt="User" />
        </DropdownMenu>
      </div>
    </header>
  );
}
```

## Routing Structure

### Next.js App Router

```
app/
├── (auth)/                 # Auth group (no dashboard layout)
│   ├── layout.tsx
│   ├── login/
│   │   └── page.tsx
│   ├── register/
│   │   └── page.tsx
│   └── forgot-password/
│       └── page.tsx
├── dashboard/             # Dashboard section
│   ├── layout.tsx
│   └── page.tsx
├── users/                 # CRUD section
│   ├── page.tsx           # List
│   ├── [id]/
│   │   ├── page.tsx       # Detail/Edit
│   │   └── loading.tsx
│   └── new/
│       └── page.tsx       # Create
├── settings/              # Settings section
│   ├── layout.tsx
│   ├── profile/
│   │   └── page.tsx
│   ├── security/
│   │   └── page.tsx
│   └── notifications/
│       └── page.tsx
└── layout.tsx             # Root layout
```

## State Management Patterns

### Data Fetching Pattern

```typescript
// app/users/page.tsx
import { Suspense } from "react";
import { UsersTable } from "@/components/users/UsersTable";
import { UsersTableSkeleton } from "@/components/users/UsersTableSkeleton";

async function getUsers() {
  // Server-side data fetching
  const res = await fetch("https://api.example.com/users", {
    cache: "no-store",
  });
  return res.json();
}

export default async function UsersPage() {
  const users = await getUsers();

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Users</h1>

      <Suspense fallback={<UsersTableSkeleton />}>
        <UsersTable data={users} />
      </Suspense>
    </div>
  );
}
```

### Client-Side State

```typescript
"use client";

import { useState, useEffect } from "react";
import { useUsers } from "@/hooks/useUsers";

export default function UsersPage() {
  const { users, isLoading, error } = useUsers();
  const [selectedUser, setSelectedUser] = useState(null);

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState error={error} />;

  return <div>{/* Page content */}</div>;
}
```

## Loading States

### Skeleton Screens

```typescript
// components/dashboard/DashboardSkeleton.tsx
export function DashboardSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-8 w-48 bg-gray-200 rounded" />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-32 bg-gray-200 rounded-lg" />
        ))}
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="h-64 bg-gray-200 rounded-lg" />
        <div className="h-64 bg-gray-200 rounded-lg" />
      </div>
    </div>
  );
}
```

### Loading Component

```typescript
// app/dashboard/loading.tsx
import { DashboardSkeleton } from "@/components/dashboard/DashboardSkeleton";

export default function Loading() {
  return <DashboardSkeleton />;
}
```

## Responsive Patterns

### Mobile Navigation

```typescript
"use client";

import { useState } from "react";
import { Sheet } from "@/components/ui/sheet";

export function MobileNav() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button onClick={() => setIsOpen(true)} className="lg:hidden">
        <MenuIcon />
      </button>

      <Sheet isOpen={isOpen} onClose={() => setIsOpen(false)}>
        <nav className="space-y-2 p-4">{/* Navigation items */}</nav>
      </Sheet>
    </>
  );
}
```
