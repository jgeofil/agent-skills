---
name: event-driven-architect
description: >-
  Designs event-driven architectures with event sourcing, CQRS, pub/sub patterns, and domain events for decoupled systems. Use when users request "event sourcing", "CQRS", "domain events", "pub/sub", or "event-driven".
license: MIT
metadata:
  version: "1.0"
  category: backend-swe
---

# Event-Driven Architect

Build decoupled, scalable systems with event-driven patterns.

## Core Workflow

1. **Identify domain events**: Define what happened
2. **Design event schema**: Structure event payloads
3. **Implement event bus**: Publish and subscribe
4. **Add event handlers**: React to events
5. **Consider CQRS**: Separate reads and writes
6. **Enable event sourcing**: Store event history

## Event Fundamentals

### Event Structure

```typescript
// events/base.ts
export interface DomainEvent<T = unknown> {
  id: string;
  type: string;
  aggregateId: string;
  aggregateType: string;
  payload: T;
  metadata: {
    timestamp: Date;
    version: number;
    correlationId?: string;
    causationId?: string;
    userId?: string;
  };
}

// Type-safe event creator
export function createEvent<T>(
  type: string,
  aggregateType: string,
  aggregateId: string,
  payload: T,
  metadata?: Partial<DomainEvent['metadata']>
): DomainEvent<T> {
  return {
    id: crypto.randomUUID(),
    type,
    aggregateType,
    aggregateId,
    payload,
    metadata: {
      timestamp: new Date(),
      version: 1,
      ...metadata,
    },
  };
}
```

### Define Domain Events

```typescript
// events/order.events.ts
export interface OrderCreatedPayload {
  customerId: string;
  items: Array<{
    productId: string;
    quantity: number;
    price: number;
  }>;
  totalAmount: number;
  shippingAddress: Address;
}

export interface OrderPaidPayload {
  paymentId: string;
  amount: number;
  method: 'card' | 'bank' | 'wallet';
}

export interface OrderShippedPayload {
  trackingNumber: string;
  carrier: string;
  estimatedDelivery: string;
}

export interface OrderCancelledPayload {
  reason: string;
  cancelledBy: string;
  refundAmount?: number;
}

// Event types
export type OrderEvent =
  | DomainEvent<OrderCreatedPayload> & { type: 'OrderCreated' }
  | DomainEvent<OrderPaidPayload> & { type: 'OrderPaid' }
  | DomainEvent<OrderShippedPayload> & { type: 'OrderShipped' }
  | DomainEvent<OrderCancelledPayload> & { type: 'OrderCancelled' };

// Event creators
export const OrderEvents = {
  created: (orderId: string, payload: OrderCreatedPayload) =>
    createEvent('OrderCreated', 'Order', orderId, payload),

  paid: (orderId: string, payload: OrderPaidPayload) =>
    createEvent('OrderPaid', 'Order', orderId, payload),

  shipped: (orderId: string, payload: OrderShippedPayload) =>
    createEvent('OrderShipped', 'Order', orderId, payload),

  cancelled: (orderId: string, payload: OrderCancelledPayload) =>
    createEvent('OrderCancelled', 'Order', orderId, payload),
};
```

## Best Practices

1. **Immutable events**: Never modify stored events
2. **Descriptive event names**: Past tense (OrderCreated, not CreateOrder)
3. **Include all context**: Events should be self-contained
4. **Version events**: Handle schema evolution
5. **Idempotent handlers**: Handle duplicate events gracefully
6. **Separate concerns**: Commands mutate, queries read
7. **Event versioning**: Support backward compatibility
8. **Dead letter queue**: Handle failed events

## Output Checklist

Every event-driven system should include:

- [ ] Well-defined domain events
- [ ] Type-safe event payloads
- [ ] Event bus (in-memory or distributed)
- [ ] Event handlers with error handling
- [ ] Event store for persistence
- [ ] Aggregate with event sourcing (if needed)
- [ ] CQRS separation (if needed)
- [ ] Read model projectors
- [ ] Dead letter handling
- [ ] Event replay capability


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

