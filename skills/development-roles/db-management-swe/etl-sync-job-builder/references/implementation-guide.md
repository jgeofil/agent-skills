# ETL/Sync Job Builder - Implementation Guide & Code Recipes

## Idempotent Upsert Pattern

```typescript
// Idempotent sync - safe to run multiple times
async function syncUsersIdempotent(users: User[]) {
  for (const user of users) {
    await prisma.user.upsert({
      where: { id: user.id },
      create: user,
      update: {
        email: user.email,
        name: user.name,
        updated_at: user.updated_at,
      },
    });
  }
}

// Batch upsert for better performance
async function syncUsersBatch(users: User[]) {
  // PostgreSQL: Use ON CONFLICT
  await prisma.$executeRaw`
    INSERT INTO users (id, email, name, updated_at)
    SELECT * FROM UNNEST(
      ${users.map((u) => u.id)}::bigint[],
      ${users.map((u) => u.email)}::text[],
      ${users.map((u) => u.name)}::text[],
      ${users.map((u) => u.updated_at)}::timestamp[]
    )
    ON CONFLICT (id) DO UPDATE SET
      email = EXCLUDED.email,
      name = EXCLUDED.name,
      updated_at = EXCLUDED.updated_at
    WHERE users.updated_at < EXCLUDED.updated_at
  `;
}
```

## Retry Logic with Exponential Backoff

```typescript
async function syncWithRetry<T>(
  operation: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      if (attempt === maxRetries) throw error;

      const delay = baseDelay * Math.pow(2, attempt);
      console.log(`  Retry ${attempt + 1}/${maxRetries} after ${delay}ms`);
      await sleep(delay);
    }
  }

  throw new Error("Max retries exceeded");
}

// Usage
await syncWithRetry(
  async () => {
    return await syncOrders();
  },
  3,
  1000
);
```

## Change Data Capture (CDC)

```typescript
// Listen to database changes
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

// PostgreSQL: Listen to logical replication
async function setupCDC() {
  await prisma.$executeRaw`
    CREATE PUBLICATION orders_publication FOR TABLE orders;
  `;

  // Subscribe to changes (using pg library)
  const client = await pg.connect();

  client.query("LISTEN orders_changed;");

  client.on("notification", async (msg) => {
    const change = JSON.parse(msg.payload);

    if (change.operation === "INSERT" || change.operation === "UPDATE") {
      await syncOrder(change.data);
    }
  });
}
```

## Conflict Resolution

```typescript
interface ConflictResolution {
  strategy: "source-wins" | "dest-wins" | "latest-wins" | "merge";
}

async function syncWithConflictResolution(
  sourceRecord: any,
  destRecord: any,
  strategy: ConflictResolution["strategy"]
) {
  if (strategy === "source-wins") {
    return sourceRecord;
  }

  if (strategy === "dest-wins") {
    return destRecord;
  }

  if (strategy === "latest-wins") {
    return sourceRecord.updated_at > destRecord.updated_at
      ? sourceRecord
      : destRecord;
  }

  if (strategy === "merge") {
    // Merge non-null fields
    return {
      ...destRecord,
      ...Object.fromEntries(
        Object.entries(sourceRecord).filter(([_, v]) => v != null)
      ),
    };
  }
}
```

## Monitoring & Observability

```typescript
// Track sync job metrics
interface SyncMetrics {
  jobName: string;
  startTime: Date;
  endTime: Date;
  recordsProcessed: number;
  recordsInserted: number;
  recordsUpdated: number;
  recordsSkipped: number;
  errors: number;
  durationMs: number;
}

async function logSyncMetrics(metrics: SyncMetrics) {
  await prisma.syncMetric.create({
    data: metrics,
  });

  console.log(`
📊 Sync Metrics
  Job: ${metrics.jobName}
  Records: ${metrics.recordsProcessed}
  Inserted: ${metrics.recordsInserted}
  Updated: ${metrics.recordsUpdated}
  Errors: ${metrics.errors}
  Duration: ${metrics.durationMs}ms
  `);
}
```

## Full ETL Job Example

```typescript
// jobs/sync-orders-to-warehouse.ts
export class OrdersETLJob extends ETLJob {
  constructor() {
    super("orders-etl", "orders_warehouse_sync");
  }

  async extract(since: Date): Promise<Order[]> {
    return prisma.order.findMany({
      where: {
        updated_at: { gt: since },
      },
      include: {
        items: true,
        user: true,
      },
      orderBy: { updated_at: "asc" },
    });
  }

  async transform(orders: Order[]): Promise<WarehouseOrder[]> {
    return orders.map((order) => ({
      order_id: order.id,
      user_email: order.user.email,
      total_amount: order.total,
      item_count: order.items.length,
      status: order.status,
      order_date: order.created_at,
      synced_at: new Date(),
    }));
  }

  async load(data: WarehouseOrder[]): Promise<void> {
    const batchSize = 100;

    for (let i = 0; i < data.length; i += batchSize) {
      const batch = data.slice(i, i + batchSize);

      await warehouseDb.$executeRaw`
        INSERT INTO orders_fact (
          order_id, user_email, total_amount, item_count,
          status, order_date, synced_at
        )
        VALUES ${batch
          .map(
            (o) => `(
          ${o.order_id}, '${o.user_email}', ${o.total_amount},
          ${o.item_count}, '${o.status}', '${o.order_date}',
          '${o.synced_at}'
        )`
          )
          .join(",")}
        ON CONFLICT (order_id) DO UPDATE SET
          total_amount = EXCLUDED.total_amount,
          status = EXCLUDED.status,
          synced_at = EXCLUDED.synced_at
      `;
    }
  }
}

// Run job
new OrdersETLJob().run();
```

## Scheduling

```typescript
// Schedule ETL jobs
import cron from "node-cron";

// Run every hour
cron.schedule("0 * * * *", async () => {
  await new OrdersETLJob().run();
});

// Run every 15 minutes
cron.schedule("*/15 * * * *", async () => {
  await syncUsersIncremental();
});

// Run nightly at 2 AM
cron.schedule("0 2 * * *", async () => {
  await fullDataSync();
});
```

## Error Handling & Recovery

```typescript
async function syncWithErrorHandling() {
  const checkpoint = await getCheckpoint();
  let processedRecords = 0;

  try {
    const records = await fetchRecords(checkpoint);

    for (const record of records) {
      try {
        await processRecord(record);
        processedRecords++;

        // Save checkpoint every 100 records
        if (processedRecords % 100 === 0) {
          await saveCheckpoint(record.id);
        }
      } catch (error) {
        // Log error but continue
        console.error(`Failed to process record ${record.id}:`, error);
        await logFailedRecord(record.id, error);
      }
    }

    await saveCheckpoint("completed");
  } catch (error) {
    // Critical failure - job will retry from checkpoint
    console.error("Job failed:", error);
    throw error;
  }
}
```
