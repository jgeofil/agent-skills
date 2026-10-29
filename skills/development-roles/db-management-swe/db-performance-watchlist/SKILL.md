---
name: db-performance-watchlist
description: >-
  Defines database performance monitoring strategy with slow query detection, resource usage alerts, query execution thresholds, and automated alerting. Use for "database monitoring", "performance alerts", "slow queries", or "DB metrics".
license: MIT
metadata:
  version: "1.0"
  category: db-management-swe
---

# DB Performance Watchlist

Monitor database performance and prevent regressions.

## Key Performance Metrics

```typescript
// performance-metrics.ts
export interface DBMetrics {
  // Query Performance
  slowQueries: {
    threshold: number; // ms
    count: number;
    queries: SlowQuery[];
  };

  // Connection Pool
  connections: {
    active: number;
    idle: number;
    total: number;
    maxConnections: number;
    utilizationPercent: number;
  };

  // Resource Usage
  resources: {
    cpuPercent: number;
    memoryPercent: number;
    diskUsagePercent: number;
    iops: number;
  };

  // Query Statistics
  queryStats: {
    selectsPerSecond: number;
    insertsPerSecond: number;
    updatesPerSecond: number;
    deletesPerSecond: number;
  };

  // Cache Performance
  cache: {
    hitRate: number; // %
    size: number; // MB
    evictions: number;
  };

  // Index Usage
  indexes: {
    unusedIndexes: string[];
    missingIndexes: string[];
  };
}

interface SlowQuery {
  query: string;
  duration: number;
  calls: number;
  avgDuration: number;
  table: string;
}
```

## Slow Query Detection

```typescript
// scripts/detect-slow-queries.ts
async function detectSlowQueries(thresholdMs: number = 100) {
  // Enable slow query logging (PostgreSQL)
  await prisma.$executeRaw`
    ALTER DATABASE mydb
    SET log_min_duration_statement = ${thresholdMs};
  `;

  // Query pg_stat_statements for slow queries
  const slowQueries = await prisma.$queryRaw<SlowQuery[]>`
    SELECT
      query,
      calls,
      total_exec_time / 1000 as total_time_ms,
      mean_exec_time / 1000 as avg_time_ms,
      max_exec_time / 1000 as max_time_ms,
      (total_exec_time / sum(total_exec_time) OVER()) * 100 as percent_of_total
    FROM pg_stat_statements
    WHERE mean_exec_time > ${thresholdMs}
    ORDER BY mean_exec_time DESC
    LIMIT 20
  `;

  console.log("🐌 Slow Queries Detected:\n");

  slowQueries.forEach((q, i) => {
    console.log(`${i + 1}. ${q.query.substring(0, 80)}...`);
    console.log(`   Calls: ${q.calls}`);
    console.log(`   Avg: ${q.avg_time_ms.toFixed(2)}ms`);
    console.log(`   Max: ${q.max_time_ms.toFixed(2)}ms`);
    console.log(`   % of total time: ${q.percent_of_total.toFixed(1)}%\n`);
  });

  return slowQueries;
}
```

## Best Practices

1. **Monitor continuously**: Don't wait for problems
2. **Set appropriate thresholds**: Based on your SLAs
3. **Alert on trends**: Not just absolute values
4. **Review regularly**: Weekly performance reviews
5. **Automate everything**: No manual checks
6. **Document baselines**: Know what's normal
7. **Test alerts**: Ensure they work

## Output Checklist

- [ ] Slow query detection configured
- [ ] Connection pool monitoring
- [ ] Resource usage tracking
- [ ] Cache hit rate monitoring
- [ ] Index usage analysis
- [ ] Alert thresholds defined
- [ ] Monitoring dashboard setup
- [ ] Automated checks scheduled
- [ ] Grafana/alerting integration
- [ ] Performance baseline documented


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

