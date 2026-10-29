---
name: multi-tenant-safety-checker
description: >-
  Ensures tenant isolation at query and policy level using Row Level Security, automated testing, and security audits. Prevents data leakage between tenants. Use for "multi-tenancy", "tenant isolation", "RLS", or "data security".
license: MIT
metadata:
  version: "1.0"
  category: db-management-swe
---

# Multi-tenant Safety Checker

Ensure complete tenant isolation and prevent data leakage.

## Row Level Security (RLS)

### PostgreSQL RLS Setup

```sql
-- Enable RLS on tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

-- Create policy for users table
CREATE POLICY tenant_isolation_policy ON users
  USING (tenant_id = current_setting('app.tenant_id')::INTEGER);

-- Create policy for orders table
CREATE POLICY tenant_isolation_policy ON orders
  USING (tenant_id = current_setting('app.tenant_id')::INTEGER);

-- Create policy for products table
CREATE POLICY tenant_isolation_policy ON products
  USING (tenant_id = current_setting('app.tenant_id')::INTEGER);

-- Force RLS even for table owners
ALTER TABLE users FORCE ROW LEVEL SECURITY;
ALTER TABLE orders FORCE ROW LEVEL SECURITY;
ALTER TABLE products FORCE ROW LEVEL SECURITY;
```

### Application-Level Tenant Context

```typescript
// middleware/tenant-context.ts
import { PrismaClient } from "@prisma/client";

export class TenantContext {
  constructor(private prisma: PrismaClient) {}

  async setTenant(tenantId: number): Promise<void> {
    await this.prisma.$executeRaw`
      SET LOCAL app.tenant_id = ${tenantId}
    `;
  }

  async withTenant<T>(
    tenantId: number,
    callback: () => Promise<T>
  ): Promise<T> {
    return this.prisma.$transaction(async (tx) => {
      // Set tenant context for this transaction
      await tx.$executeRaw`SET LOCAL app.tenant_id = ${tenantId}`;

      // Execute queries within tenant context
      return callback();
    });
  }
}

// Usage in API route
app.get("/api/orders", async (req, res) => {
  const tenantId = req.user.tenantId;

  const orders = await tenantContext.withTenant(tenantId, async () => {
    return prisma.order.findMany(); // Automatically filtered by RLS
  });

  res.json(orders);
});
```

## Tenant Isolation Checklist

```markdown
# Multi-tenant Security Checklist


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

