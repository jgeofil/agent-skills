# DB Performance Watchlist - Implementation Guide & Code Recipes

## Connection Pool Monitoring

```typescript
async function monitorConnectionPool() {
  const stats = await prisma.$queryRaw<any[]>`
    SELECT
      sum(numbackends) as total_connections,
      sum(CASE WHEN state = 'active' THEN 1 ELSE 0 END) as active,
      sum(CASE WHEN state = 'idle' THEN 1 ELSE 0 END) as idle,
      max_connections
    FROM pg_stat_database
    CROSS JOIN (SELECT setting::int as max_connections FROM pg_settings WHERE name = 'max_connections')
    WHERE datname = current_database()
    GROUP BY max_connections
  `;

  const { total_connections, active, idle, max_connections } = stats[0];
  const utilization = (total_connections / max_connections) * 100;

  console.log("🔌 Connection Pool Status:");
  console.log(
    `  Total: ${total_connections}/${max_connections} (${utilization.toFixed(
      1
    )}%)`
  );
  console.log(`  Active: ${active}`);
  console.log(`  Idle: ${idle}`);

  // Alert if > 80% utilization
  if (utilization > 80) {
    console.warn("⚠️  Connection pool >80% utilized!");
    await sendAlert({
      title: "High connection pool usage",
      message: `${utilization.toFixed(1)}% of connections in use`,
    });
  }
}
```

## Resource Monitoring

```typescript
async function monitorResources() {
  // CPU Usage
  const cpuStats = await prisma.$queryRaw<any[]>`
    SELECT
      (sum(total_exec_time) / (extract(epoch from (now() - stats_reset)) * 1000 * 100)) as cpu_percent
    FROM pg_stat_statements, pg_stat_database
    WHERE datname = current_database()
  `;

  // Memory Usage
  const memStats = await prisma.$queryRaw<any[]>`
    SELECT
      pg_size_pretty(pg_database_size(current_database())) as db_size,
      pg_size_pretty(sum(pg_relation_size(schemaname||'.'||tablename))) as tables_size
    FROM pg_tables
    WHERE schemaname = 'public'
  `;

  // Cache Hit Rate
  const cacheStats = await prisma.$queryRaw<any[]>`
    SELECT
      sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) * 100 as cache_hit_rate
    FROM pg_statio_user_tables
  `;

  console.log("📊 Resource Usage:");
  console.log(`  CPU: ${cpuStats[0].cpu_percent.toFixed(1)}%`);
  console.log(`  Database Size: ${memStats[0].db_size}`);
  console.log(`  Cache Hit Rate: ${cacheStats[0].cache_hit_rate.toFixed(1)}%`);

  // Alert if cache hit rate < 90%
  if (cacheStats[0].cache_hit_rate < 90) {
    console.warn("⚠️  Cache hit rate below 90%!");
    await sendAlert({
      title: "Low cache hit rate",
      message: `Cache hit rate: ${cacheStats[0].cache_hit_rate.toFixed(1)}%`,
    });
  }
}
```

## Index Usage Analysis

```typescript
async function analyzeIndexUsage() {
  // Find unused indexes
  const unusedIndexes = await prisma.$queryRaw<any[]>`
    SELECT
      schemaname,
      tablename,
      indexname,
      idx_scan
    FROM pg_stat_user_indexes
    WHERE idx_scan = 0
    AND indexname NOT LIKE '%_pkey'
    ORDER BY pg_relation_size(indexrelid) DESC
  `;

  console.log("🗂️  Unused Indexes:\n");
  unusedIndexes.forEach((idx) => {
    console.log(`  ${idx.tablename}.${idx.indexname} (0 scans)`);
  });

  // Find missing indexes (sequential scans on large tables)
  const missingIndexes = await prisma.$queryRaw<any[]>`
    SELECT
      schemaname,
      tablename,
      seq_scan,
      seq_tup_read,
      idx_scan,
      n_live_tup
    FROM pg_stat_user_tables
    WHERE seq_scan > 1000
    AND n_live_tup > 10000
    ORDER BY seq_scan * n_live_tup DESC
    LIMIT 10
  `;

  console.log("\n📉 Tables with High Sequential Scans:\n");
  missingIndexes.forEach((table) => {
    console.log(`  ${table.tablename}:`);
    console.log(`    Sequential scans: ${table.seq_scan}`);
    console.log(`    Rows: ${table.n_live_tup}`);
    console.log(`    Index scans: ${table.idx_scan}`);
  });
}
```

## Alert Thresholds

```typescript
const ALERT_THRESHOLDS = {
  slowQuery: {
    avgDuration: 500, // ms
    maxDuration: 2000, // ms
    callsPerMinute: 100,
  },
  connections: {
    utilizationWarning: 70, // %
    utilizationCritical: 85, // %
  },
  resources: {
    cpuWarning: 70, // %
    cpuCritical: 85, // %
    memoryWarning: 80, // %
    memoryCritical: 90, // %
    diskWarning: 75, // %
    diskCritical: 85, // %
  },
  cache: {
    hitRateWarning: 90, // %
    hitRateCritical: 80, // %
  },
  queryRate: {
    maxSelectsPerSecond: 10000,
    maxWritesPerSecond: 1000,
  },
};

async function checkThresholds() {
  const metrics = await gatherMetrics();

  // Check slow queries
  if (metrics.slowQueries.count > 10) {
    await sendAlert({
      level: "warning",
      title: "Slow queries detected",
      message: `${metrics.slowQueries.count} queries exceeding ${ALERT_THRESHOLDS.slowQuery.avgDuration}ms`,
    });
  }

  // Check connection pool
  if (
    metrics.connections.utilizationPercent >
    ALERT_THRESHOLDS.connections.utilizationCritical
  ) {
    await sendAlert({
      level: "critical",
      title: "Connection pool critical",
      message: `${metrics.connections.utilizationPercent.toFixed(
        1
      )}% utilization`,
    });
  }

  // Check cache hit rate
  if (metrics.cache.hitRate < ALERT_THRESHOLDS.cache.hitRateCritical) {
    await sendAlert({
      level: "critical",
      title: "Cache hit rate critical",
      message: `${metrics.cache.hitRate.toFixed(1)}% hit rate`,
    });
  }
}
```

## Monitoring Dashboard

```typescript
// Generate monitoring report
async function generatePerformanceReport() {
  console.log("📊 Database Performance Report\n");
  console.log("=".repeat(50) + "\n");

  // Slow queries
  const slowQueries = await detectSlowQueries(100);
  console.log(`Slow Queries (>100ms): ${slowQueries.length}\n`);

  // Connection pool
  await monitorConnectionPool();
  console.log();

  // Resources
  await monitorResources();
  console.log();

  // Index usage
  await analyzeIndexUsage();
  console.log();

  // Query rates
  const queryStats = await prisma.$queryRaw<any[]>`
    SELECT
      sum(xact_commit + xact_rollback) as transactions,
      sum(tup_returned) as rows_read,
      sum(tup_inserted) as rows_inserted,
      sum(tup_updated) as rows_updated,
      sum(tup_deleted) as rows_deleted
    FROM pg_stat_database
    WHERE datname = current_database()
  `;

  console.log("📈 Query Statistics:");
  console.log(`  Transactions: ${queryStats[0].transactions}`);
  console.log(`  Rows read: ${queryStats[0].rows_read}`);
  console.log(`  Rows inserted: ${queryStats[0].rows_inserted}`);
  console.log(`  Rows updated: ${queryStats[0].rows_updated}`);
  console.log(`  Rows deleted: ${queryStats[0].rows_deleted}`);
}
```

## Automated Monitoring Script

```typescript
// scripts/monitor-db.ts
import cron from "node-cron";

// Run every 5 minutes
cron.schedule("*/5 * * * *", async () => {
  await checkThresholds();
});

// Generate report every hour
cron.schedule("0 * * * *", async () => {
  await generatePerformanceReport();
});

// Analyze indexes weekly
cron.schedule("0 0 * * 0", async () => {
  await analyzeIndexUsage();
});
```

## Grafana Dashboard Queries

```sql
-- Query latency over time
SELECT
  bucket,
  AVG(mean_exec_time) as avg_latency,
  MAX(max_exec_time) as max_latency,
  SUM(calls) as total_calls
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat_statements%'
GROUP BY time_bucket('5 minutes', queryid)
ORDER BY bucket;

-- Connection count over time
SELECT
  now() as time,
  count(*) as total,
  count(*) FILTER (WHERE state = 'active') as active,
  count(*) FILTER (WHERE state = 'idle') as idle
FROM pg_stat_activity;

-- Cache hit rate
SELECT
  sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) * 100 as cache_hit_rate
FROM pg_statio_user_tables;
```
