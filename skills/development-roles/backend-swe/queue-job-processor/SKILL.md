---
name: queue-job-processor
description: >-
  Implements background job processing with BullMQ/Redis including job queues, workers, scheduling, retries, and monitoring. Use when users request "background jobs", "queue processing", "async tasks", "BullMQ", or "job scheduler".
license: MIT
metadata:
  version: "1.0"
  category: backend-swe
---

# Queue Job Processor

Build robust background job processing with BullMQ and Redis.

## Core Workflow

1. **Setup Redis**: Configure connection
2. **Create queues**: Define job queues
3. **Implement workers**: Process jobs
4. **Add job types**: Type-safe job definitions
5. **Configure retries**: Handle failures
6. **Add monitoring**: Dashboard and alerts

## Installation

```bash
npm install bullmq ioredis
npm install -D @types/ioredis
```

## Redis Connection

```typescript
// lib/redis.ts
import IORedis from 'ioredis';

export const redis = new IORedis(process.env.REDIS_URL!, {
  maxRetriesPerRequest: null, // Required for BullMQ
  enableReadyCheck: false,
});

export const redisSubscriber = new IORedis(process.env.REDIS_URL!, {
  maxRetriesPerRequest: null,
  enableReadyCheck: false,
});
```

## Queue Setup

### Define Job Types

```typescript
// jobs/types.ts
export interface EmailJobData {
  to: string;
  subject: string;
  template: string;
  variables: Record<string, string>;
}

export interface ImageProcessingJobData {
  imageId: string;
  userId: string;
  operations: Array<{
    type: 'resize' | 'crop' | 'watermark';
    params: Record<string, any>;
  }>;
}

export interface ReportJobData {
  reportId: string;
  userId: string;
  type: 'daily' | 'weekly' | 'monthly';
  dateRange: {
    start: string;
    end: string;
  };
}

export interface WebhookJobData {
  url: string;
  payload: Record<string, any>;
  headers?: Record<string, string>;
  retryCount?: number;
}

export type JobData =
  | { type: 'email'; data: EmailJobData }
  | { type: 'image-processing'; data: ImageProcessingJobData }
  | { type: 'report'; data: ReportJobData }
  | { type: 'webhook'; data: WebhookJobData };
```

### Create Queues

```typescript
// queues/index.ts
import { Queue, QueueOptions } from 'bullmq';
import { redis } from '../lib/redis';
import {
  EmailJobData,
  ImageProcessingJobData,
  ReportJobData,
  WebhookJobData,
} from './types';

const defaultOptions: QueueOptions = {
  connection: redis,
  defaultJobOptions: {
    attempts: 3,
    backoff: {
      type: 'exponential',
      delay: 1000,
    },
    removeOnComplete: {
      count: 1000, // Keep last 1000 completed jobs
      age: 24 * 3600, // Keep for 24 hours
    },
    removeOnFail: {
      count: 5000, // Keep last 5000 failed jobs
    },
  },
};

export const emailQueue = new Queue<EmailJobData>('email', defaultOptions);

export const imageQueue = new Queue<ImageProcessingJobData>('image-processing', {
  ...defaultOptions,
  defaultJobOptions: {
    ...defaultOptions.defaultJobOptions,
    attempts: 5,
    timeout: 5 * 60 * 1000, // 5 minutes
  },
});

export const reportQueue = new Queue<ReportJobData>('reports', {
  ...defaultOptions,
  defaultJobOptions: {
    ...defaultOptions.defaultJobOptions,
    timeout: 30 * 60 * 1000, // 30 minutes
  },
});

export const webhookQueue = new Queue<WebhookJobData>('webhooks', {
  ...defaultOptions,
  defaultJobOptions: {
    ...defaultOptions.defaultJobOptions,
    attempts: 5,
    backoff: {
      type: 'exponential',
      delay: 5000,
    },
  },
});
```

## Best Practices

1. **Idempotent jobs**: Jobs should be safe to retry
2. **Unique job IDs**: Prevent duplicate processing
3. **Set timeouts**: Prevent stuck jobs
4. **Use progress updates**: For long-running jobs
5. **Handle failures gracefully**: Alert and log
6. **Clean up old jobs**: Remove completed/failed jobs
7. **Graceful shutdown**: Wait for jobs to complete
8. **Monitor queues**: Use Bull Board or similar

## Output Checklist

Every queue implementation should include:

- [ ] Redis connection with proper config
- [ ] Typed job data interfaces
- [ ] Queue with default options
- [ ] Worker with concurrency limits
- [ ] Retry and backoff configuration
- [ ] Event handlers for monitoring
- [ ] Error handling (retryable vs non-retryable)
- [ ] Graceful shutdown handling
- [ ] Bull Board or monitoring dashboard
- [ ] Scheduled/recurring jobs (if needed)


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)
- [Job Design Patterns](references/job-design-patterns.md)
- [Python Celery Rq](references/python-celery-rq.md)

