# React Server Components - Implementation Guide & Code Recipes

## Data Fetching Patterns

### Parallel Data Fetching

```tsx
// app/page.tsx
async function getUser(id: string) {
  const res = await fetch(`/api/users/${id}`);
  return res.json();
}

async function getPosts(userId: string) {
  const res = await fetch(`/api/users/${userId}/posts`);
  return res.json();
}

async function getComments(userId: string) {
  const res = await fetch(`/api/users/${userId}/comments`);
  return res.json();
}

export default async function ProfilePage({ params }: { params: { id: string } }) {
  // Parallel fetching - all requests start simultaneously
  const [user, posts, comments] = await Promise.all([
    getUser(params.id),
    getPosts(params.id),
    getComments(params.id),
  ]);

  return (
    <div>
      <UserHeader user={user} />
      <PostsList posts={posts} />
      <CommentsList comments={comments} />
    </div>
  );
}
```

### Sequential Data Fetching (When Dependent)

```tsx
export default async function OrderPage({ params }: { params: { id: string } }) {
  // Sequential - second fetch depends on first
  const order = await getOrder(params.id);
  const customer = await getCustomer(order.customerId);

  return (
    <div>
      <OrderDetails order={order} />
      <CustomerInfo customer={customer} />
    </div>
  );
}
```

### Caching and Revalidation

```tsx
// Static data (cached indefinitely)
async function getStaticData() {
  const res = await fetch('https://api.example.com/static', {
    cache: 'force-cache', // Default
  });
  return res.json();
}

// Dynamic data (no cache)
async function getDynamicData() {
  const res = await fetch('https://api.example.com/dynamic', {
    cache: 'no-store',
  });
  return res.json();
}

// Revalidate after time
async function getRevalidatedData() {
  const res = await fetch('https://api.example.com/data', {
    next: { revalidate: 3600 }, // Revalidate every hour
  });
  return res.json();
}

// Revalidate by tag
async function getTaggedData() {
  const res = await fetch('https://api.example.com/products', {
    next: { tags: ['products'] },
  });
  return res.json();
}

// Trigger revalidation
import { revalidateTag } from 'next/cache';
revalidateTag('products');
```

## Streaming with Suspense

### Page-Level Streaming

```tsx
// app/dashboard/page.tsx
import { Suspense } from 'react';
import { StatsCards, StatsCardsSkeleton } from './StatsCards';
import { RecentOrders, RecentOrdersSkeleton } from './RecentOrders';
import { TopProducts, TopProductsSkeleton } from './TopProducts';

export default function DashboardPage() {
  return (
    <div>
      <h1>Dashboard</h1>

      {/* Each section streams independently */}
      <Suspense fallback={<StatsCardsSkeleton />}>
        <StatsCards />
      </Suspense>

      <div className="grid grid-cols-2 gap-4 mt-8">
        <Suspense fallback={<RecentOrdersSkeleton />}>
          <RecentOrders />
        </Suspense>

        <Suspense fallback={<TopProductsSkeleton />}>
          <TopProducts />
        </Suspense>
      </div>
    </div>
  );
}
```

### Component with Data

```tsx
// app/dashboard/StatsCards.tsx
import { db } from '@/lib/db';

async function getStats() {
  // Simulate slow query
  await new Promise((resolve) => setTimeout(resolve, 2000));
  return db.stats.findFirst();
}

export async function StatsCards() {
  const stats = await getStats();

  return (
    <div className="grid grid-cols-4 gap-4">
      <Card title="Revenue" value={stats.revenue} />
      <Card title="Orders" value={stats.orders} />
      <Card title="Customers" value={stats.customers} />
      <Card title="Products" value={stats.products} />
    </div>
  );
}

export function StatsCardsSkeleton() {
  return (
    <div className="grid grid-cols-4 gap-4">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="h-24 bg-gray-200 animate-pulse rounded" />
      ))}
    </div>
  );
}
```

### Loading States

```tsx
// app/products/loading.tsx
export default function ProductsLoading() {
  return (
    <div className="grid grid-cols-3 gap-4">
      {[...Array(9)].map((_, i) => (
        <div key={i} className="h-64 bg-gray-200 animate-pulse rounded" />
      ))}
    </div>
  );
}
```

## Server Actions

### Form Actions

```tsx
// app/contact/page.tsx
import { submitContact } from './actions';

export default function ContactPage() {
  return (
    <form action={submitContact}>
      <input name="email" type="email" required />
      <textarea name="message" required />
      <button type="submit">Send</button>
    </form>
  );
}
```

```tsx
// app/contact/actions.ts
'use server';

import { z } from 'zod';
import { revalidatePath } from 'next/cache';

const schema = z.object({
  email: z.string().email(),
  message: z.string().min(10),
});

export async function submitContact(formData: FormData) {
  const validatedFields = schema.safeParse({
    email: formData.get('email'),
    message: formData.get('message'),
  });

  if (!validatedFields.success) {
    return { error: validatedFields.error.flatten().fieldErrors };
  }

  await db.contact.create({
    data: validatedFields.data,
  });

  revalidatePath('/contacts');
  return { success: true };
}
```

### With useActionState

```tsx
// components/ContactForm.tsx
'use client';

import { useActionState } from 'react';
import { submitContact } from '@/app/contact/actions';

export function ContactForm() {
  const [state, formAction, isPending] = useActionState(submitContact, null);

  return (
    <form action={formAction}>
      <input name="email" type="email" required />
      {state?.error?.email && <p className="text-red-500">{state.error.email}</p>}

      <textarea name="message" required />
      {state?.error?.message && <p className="text-red-500">{state.error.message}</p>}

      <button type="submit" disabled={isPending}>
        {isPending ? 'Sending...' : 'Send'}
      </button>

      {state?.success && <p className="text-green-500">Message sent!</p>}
    </form>
  );
}
```

## Optimistic Updates

```tsx
// components/LikeButton.tsx
'use client';

import { useOptimistic, useTransition } from 'react';
import { likePost } from '@/app/actions';

interface LikeButtonProps {
  postId: string;
  initialLikes: number;
  isLiked: boolean;
}

export function LikeButton({ postId, initialLikes, isLiked }: LikeButtonProps) {
  const [isPending, startTransition] = useTransition();
  const [optimisticState, addOptimistic] = useOptimistic(
    { likes: initialLikes, isLiked },
    (state, newIsLiked: boolean) => ({
      likes: newIsLiked ? state.likes + 1 : state.likes - 1,
      isLiked: newIsLiked,
    })
  );

  const handleClick = () => {
    startTransition(async () => {
      addOptimistic(!optimisticState.isLiked);
      await likePost(postId);
    });
  };

  return (
    <button onClick={handleClick} disabled={isPending}>
      {optimisticState.isLiked ? '❤️' : '🤍'} {optimisticState.likes}
    </button>
  );
}
```

## Patterns for Common Use Cases

### Authentication Check

```tsx
// app/dashboard/layout.tsx
import { redirect } from 'next/navigation';
import { getSession } from '@/lib/auth';

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getSession();

  if (!session) {
    redirect('/login');
  }

  return (
    <div>
      <nav>Welcome, {session.user.name}</nav>
      {children}
    </div>
  );
}
```

### Passing Server Data to Client

```tsx
// app/products/[id]/page.tsx
import { getProduct } from '@/lib/products';
import { ProductGallery } from './ProductGallery';

export default async function ProductPage({ params }: { params: { id: string } }) {
  const product = await getProduct(params.id);

  return (
    <div>
      <h1>{product.name}</h1>
      <p>{product.description}</p>

      {/* Pass serializable data to client component */}
      <ProductGallery
        images={product.images}
        initialIndex={0}
      />
    </div>
  );
}
```

### Nested Client Components

```tsx
// components/Modal.tsx
'use client';

import { createContext, useContext, useState } from 'react';

const ModalContext = createContext<{
  open: boolean;
  setOpen: (open: boolean) => void;
} | null>(null);

export function ModalProvider({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  return (
    <ModalContext.Provider value={{ open, setOpen }}>
      {children}
    </ModalContext.Provider>
  );
}

export function useModal() {
  const context = useContext(ModalContext);
  if (!context) throw new Error('useModal must be used within ModalProvider');
  return context;
}
```
