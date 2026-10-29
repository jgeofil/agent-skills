---
name: etl-sync-job-builder
description: >-
  Designs reliable ETL and data synchronization jobs with incremental updates, idempotency guarantees, watermark tracking, error handling, and retry logic. Use for "ETL jobs", "data sync", "incremental sync", or "data pipeline".
license: MIT
metadata:
  version: "1.0"
  category: db-management-swe
---

# ETL/Sync Job Builder

Build reliable, incremental data synchronization pipelines.

## ETL Job Pattern

```typescript
// jobs/sync-users.ts
interface SyncJob {
  name: string;
  source: "database" | "api" | "file";
  destination: "database" | "warehouse" | "s3";
  schedule: string;
}

export class ETLJob {
  constructor(private name: string, private watermarkKey: string) {}

  async run() {
    console.log(`🔄 Starting ${this.name}...`);

    try {
      // 1. Get last watermark
      const lastSync = await this.getWatermark();
      console.log(`  Last sync: ${lastSync}`);

      // 2. Extract data
      const data = await this.extract(lastSync);
      console.log(`  Extracted ${data.length} records`);

      // 3. Transform data
      const transformed = await this.transform(data);

      // 4. Load data
      await this.load(transformed);

      // 5. Update watermark
      await this.updateWatermark(new Date());

      console.log(`✅ ${this.name} complete`);
    } catch (error) {
      console.error(`❌ ${this.name} failed:`, error);
      throw error;
    }
  }

  private async extract(since: Date) {
    // Extract logic
    return [];
  }

  private async transform(data: any[]) {
    // Transform logic
    return data;
  }

  private async load(data: any[]) {
    // Load logic
  }

  private async getWatermark(): Promise<Date> {
    const watermark = await prisma.syncWatermark.findUnique({
      where: { key: this.watermarkKey },
    });
    return watermark?.lastSync || new Date(0);
  }

  private async updateWatermark(timestamp: Date) {
    await prisma.syncWatermark.upsert({
      where: { key: this.watermarkKey },
      create: { key: this.watermarkKey, lastSync: timestamp },
      update: { lastSync: timestamp },
    });
  }
}
```

## Watermark Strategy

```prisma
// Track sync progress
model SyncWatermark {
  key      String   @id
  lastSync DateTime
  metadata Json?

  @@index([lastSync])
}
```

```typescript
// Incremental sync using watermark
async function syncOrdersIncremental() {
  // Get last sync time
  const watermark = await prisma.syncWatermark.findUnique({
    where: { key: "orders_sync" },
  });

  const lastSync = watermark?.lastSync || new Date(0);

  // Fetch only new/updated records
  const newOrders = await sourceDb.order.findMany({
    where: {
      updated_at: { gt: lastSync },
    },
    orderBy: { updated_at: "asc" },
  });

  console.log(`📦 Syncing ${newOrders.length} orders...`);

  // Process in batches
  for (let i = 0; i < newOrders.length; i += 100) {
    const batch = newOrders.slice(i, i + 100);

    await destinationDb.order.createMany({
      data: batch,
      skipDuplicates: true, // Idempotency
    });
  }

  // Update watermark to latest record
  if (newOrders.length > 0) {
    const latestTimestamp = newOrders[newOrders.length - 1].updated_at;

    await prisma.syncWatermark.upsert({
      where: { key: "orders_sync" },
      create: { key: "orders_sync", lastSync: latestTimestamp },
      update: { lastSync: latestTimestamp },
    });
  }

  console.log(`✅ Sync complete`);
}
```

## Best Practices

1. **Incremental sync**: Use watermarks, don't full-scan
2. **Idempotent operations**: Safe to retry
3. **Batch processing**: Process 100-1000 records at a time
4. **Checkpointing**: Resume from failure point
5. **Retry with backoff**: Handle transient failures
6. **Monitor metrics**: Track job health
7. **Test thoroughly**: Including failure scenarios

## Output Checklist

- [ ] ETL job class created
- [ ] Watermark tracking implemented
- [ ] Incremental sync logic
- [ ] Idempotent upsert operations
- [ ] Retry logic with backoff
- [ ] Conflict resolution strategy
- [ ] Monitoring and metrics
- [ ] Error handling and recovery
- [ ] Job scheduling configured
- [ ] Testing including failure cases


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

