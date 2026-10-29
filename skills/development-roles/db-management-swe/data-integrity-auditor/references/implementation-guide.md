# Data Integrity Auditor - Implementation Guide & Code Recipes

## Automated Fixes

```typescript
// scripts/fix-integrity-issues.ts
async function fixOrphanedRecords() {
  console.log("🔧 Fixing orphaned records...\n");

  // Delete orphaned orders
  const deletedOrders = await prisma.$executeRaw`
    DELETE FROM orders
    WHERE id IN (
      SELECT o.id FROM orders o
      LEFT JOIN users u ON u.id = o.user_id
      WHERE u.id IS NULL
    )
  `;
  console.log(`✅ Deleted ${deletedOrders} orphaned orders`);

  // Delete orphaned order items
  const deletedItems = await prisma.$executeRaw`
    DELETE FROM order_items
    WHERE id IN (
      SELECT oi.id FROM order_items oi
      LEFT JOIN orders o ON o.id = oi.order_id
      WHERE o.id IS NULL
    )
  `;
  console.log(`✅ Deleted ${deletedItems} orphaned order items`);
}

async function fixDuplicates() {
  console.log("🔧 Fixing duplicate records...\n");

  // Keep newest user, delete old duplicates
  await prisma.$executeRaw`
    DELETE FROM users
    WHERE id IN (
      SELECT id FROM (
        SELECT id,
               ROW_NUMBER() OVER (PARTITION BY email ORDER BY created_at DESC) as rn
        FROM users
      ) t
      WHERE rn > 1
    )
  `;
  console.log(`✅ Fixed duplicate emails`);
}

async function fixConstraintViolations() {
  console.log("🔧 Fixing constraint violations...\n");

  // Fix negative prices
  const fixedPrices = await prisma.$executeRaw`
    UPDATE products
    SET price = ABS(price)
    WHERE price < 0
  `;
  console.log(`✅ Fixed ${fixedPrices} negative prices`);

  // Fix negative stock
  const fixedStock = await prisma.$executeRaw`
    UPDATE products
    SET stock = 0
    WHERE stock < 0
  `;
  console.log(`✅ Fixed ${fixedStock} negative stock values`);
}
```

## Prevention: Add Missing Constraints

```sql
-- Migration to add missing constraints

-- 1. Add foreign key constraints
ALTER TABLE orders
  ADD CONSTRAINT fk_orders_user_id
  FOREIGN KEY (user_id) REFERENCES users(id)
  ON DELETE CASCADE;

ALTER TABLE order_items
  ADD CONSTRAINT fk_order_items_order_id
  FOREIGN KEY (order_id) REFERENCES orders(id)
  ON DELETE CASCADE;

-- 2. Add check constraints
ALTER TABLE products
  ADD CONSTRAINT chk_products_price_positive
  CHECK (price >= 0);

ALTER TABLE products
  ADD CONSTRAINT chk_products_stock_non_negative
  CHECK (stock >= 0);

-- 3. Add unique constraints
CREATE UNIQUE INDEX idx_users_email_unique
  ON users(LOWER(email));

-- 4. Add NOT NULL constraints
ALTER TABLE users
  ALTER COLUMN email SET NOT NULL;

ALTER TABLE orders
  ALTER COLUMN total SET NOT NULL;
```

## Automated Testing

```typescript
// tests/data-integrity.test.ts
describe("Data Integrity", () => {
  it("should not allow orphaned orders", async () => {
    // Try to create order with non-existent user
    await expect(
      prisma.order.create({
        data: {
          userId: 99999, // Non-existent
          total: 100,
          status: "pending",
        },
      })
    ).rejects.toThrow("Foreign key constraint");
  });

  it("should not allow negative prices", async () => {
    await expect(
      prisma.product.create({
        data: {
          name: "Test",
          price: -10, // Invalid
          stock: 100,
        },
      })
    ).rejects.toThrow("Check constraint");
  });

  it("should not allow duplicate emails", async () => {
    await prisma.user.create({
      data: { email: "test@example.com", name: "Test" },
    });

    await expect(
      prisma.user.create({
        data: { email: "test@example.com", name: "Test 2" },
      })
    ).rejects.toThrow("Unique constraint");
  });
});
```

## Monitoring Dashboard

```typescript
// Monitor data quality metrics
async function getDataQualityMetrics() {
  return {
    orphanedOrders: await prisma.$queryRaw`
      SELECT COUNT(*) FROM orders o
      LEFT JOIN users u ON u.id = o.user_id
      WHERE u.id IS NULL
    `,
    duplicateEmails: await prisma.$queryRaw`
      SELECT COUNT(*) FROM (
        SELECT email FROM users GROUP BY email HAVING COUNT(*) > 1
      ) t
    `,
    invalidPrices: await prisma.$queryRaw`
      SELECT COUNT(*) FROM products WHERE price < 0
    `,
    missingData: await prisma.$queryRaw`
      SELECT
        SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) as users_no_email,
        SUM(CASE WHEN total IS NULL THEN 1 ELSE 0 END) as orders_no_total
      FROM users
      CROSS JOIN orders
    `,
  };
}
```
