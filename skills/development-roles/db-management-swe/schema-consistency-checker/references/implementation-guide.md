# Schema Consistency Checker - Implementation Guide & Code Recipes

## Recommended Schema Standards

```prisma
// schema.prisma with best practices

model User {
  // 1. ID: Consistent type (Int or String/cuid)
  id        Int      @id @default(autoincrement())

  // 2. Critical fields: NOT NULL
  email     String   @unique
  name      String

  // 3. Optional fields: Clearly nullable
  phone     String?
  bio       String?

  // 4. Audit timestamps: Always include
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  // 5. Relations: Proper foreign keys
  orders    Order[]

  // 6. Indexes: On frequently queried fields
  @@index([email])
  @@index([createdAt])
}

model Order {
  id        Int      @id @default(autoincrement())

  // Foreign key with clear naming
  userId    Int
  user      User     @relation(fields: [userId], references: [id])

  // Enum for status (type safety)
  status    OrderStatus @default(PENDING)

  // Decimal for money
  total     Decimal  @db.Decimal(10, 2)

  // Timestamps
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  // Indexes on foreign keys
  @@index([userId])
  @@index([status])
  @@index([createdAt])
}

enum OrderStatus {
  PENDING
  PAID
  SHIPPED
  DELIVERED
  CANCELLED
}
```

## Auto-fix Migrations

```typescript
// scripts/fix-schema.ts
async function generateFixMigrations(violations: Violation[]) {
  const migrations: string[] = [];

  violations.forEach((v) => {
    if (v.category === "nullability" && v.column) {
      migrations.push(
        `ALTER TABLE "${v.table}" ALTER COLUMN "${v.column}" SET NOT NULL;`
      );
    }

    if (
      v.category === "performance" &&
      v.recommendation.startsWith("CREATE INDEX")
    ) {
      migrations.push(v.recommendation + ";");
    }

    if (v.category === "audit" && v.message.includes("created_at")) {
      migrations.push(
        `ALTER TABLE "${v.table}" ADD COLUMN "created_at" TIMESTAMP NOT NULL DEFAULT NOW();`
      );
    }
  });

  console.log("-- Auto-generated fixes\n");
  migrations.forEach((m) => console.log(m));
}
```
