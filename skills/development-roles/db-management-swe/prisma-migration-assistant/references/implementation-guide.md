# Prisma Migration Assistant - Implementation Guide & Code Recipes

## Migration Sequencing

```markdown
# Migration Sequence: Add User Roles

## Phase 1: Additive (Week 1)

1. Add optional `role` field
2. Deploy application code that handles NULL roles
3. Backfill existing users with default role

## Phase 2: Enforcement (Week 2)

1. Make `role` field required
2. Deploy code that requires role on creation
3. Add database constraint

## Phase 3: Cleanup (Week 3)

1. Remove old permission checking code
2. Verify all users have roles
```

## Backfill Strategies

### Small Table (< 10k rows)

```typescript
// scripts/backfill-user-roles.ts
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

async function backfillUserRoles() {
  const usersWithoutRoles = await prisma.user.findMany({
    where: { role: null },
  });

  console.log(`Backfilling ${usersWithoutRoles.length} users...`);

  // Single transaction for small dataset
  await prisma.$transaction(
    usersWithoutRoles.map((user) =>
      prisma.user.update({
        where: { id: user.id },
        data: { role: "USER" }, // Default role
      })
    )
  );

  console.log("✅ Backfill complete");
}

backfillUserRoles();
```

### Large Table (> 10k rows)

```typescript
// scripts/backfill-large-table.ts
async function backfillBatched() {
  const batchSize = 1000;
  let processed = 0;
  let hasMore = true;

  while (hasMore) {
    const batch = await prisma.user.findMany({
      where: { role: null },
      take: batchSize,
      select: { id: true },
    });

    if (batch.length === 0) {
      hasMore = false;
      break;
    }

    // Process batch
    await prisma.$transaction(
      batch.map((user) =>
        prisma.user.update({
          where: { id: user.id },
          data: { role: "USER" },
        })
      )
    );

    processed += batch.length;
    console.log(`Processed ${processed} users...`);

    // Rate limiting
    await new Promise((resolve) => setTimeout(resolve, 100));
  }

  console.log(`✅ Backfilled ${processed} users`);
}
```

## Rollback Guidance

```sql
-- migrations/20240115_add_role/rollback.sql

-- Rollback Step 1: Add back old structure (if needed)
ALTER TABLE "User" DROP COLUMN "role";

-- Rollback Step 2: Restore old logic
-- (Deploy previous application version)

-- Note: Data loss consideration
-- If you backfilled data, document what was lost
```

## Migration Testing

```typescript
// tests/migrations/split-name.test.ts
import { PrismaClient } from "@prisma/client";
import { execSync } from "child_process";

describe("Split name migration", () => {
  let prisma: PrismaClient;

  beforeAll(async () => {
    // Setup test database
    execSync("npx prisma migrate deploy", {
      env: { DATABASE_URL: process.env.TEST_DATABASE_URL },
    });
    prisma = new PrismaClient();
  });

  it("should split name correctly", async () => {
    // Create user with old schema
    await prisma.$executeRaw`
      INSERT INTO "User" (name) VALUES ('John Doe')
    `;

    // Run migration
    execSync("npx prisma migrate deploy");

    // Verify split
    const user = await prisma.user.findFirst();
    expect(user?.firstName).toBe("John");
    expect(user?.lastName).toBe("Doe");
  });

  it("should handle single name", async () => {
    await prisma.$executeRaw`
      INSERT INTO "User" (name) VALUES ('Madonna')
    `;

    execSync("npx prisma migrate deploy");

    const user = await prisma.user.findFirst({
      where: { firstName: "Madonna" },
    });
    expect(user?.lastName).toBe("");
  });
});
```
