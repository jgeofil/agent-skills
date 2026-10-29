---
name: api-contract-normalizer
description: >-
  Unifies API response patterns across endpoints including pagination format, error structure, status codes, response envelopes, and versioning strategy. Provides contract documentation, shared TypeScript types, middleware utilities, and migration plan. Use when standardizing "API contracts", "response formats", "API conventions", or "API consistency".
license: MIT
metadata:
  version: "1.0"
  category: backend-swe
---

# API Contract Normalizer

Standardize API contracts across all endpoints for consistency and developer experience.

## Core Workflow

1. **Audit existing APIs**: Document current inconsistencies
2. **Define standards**: Response format, pagination, errors, status codes
3. **Create shared types**: TypeScript interfaces for all contracts
4. **Build middleware**: Normalize responses automatically
5. **Document contract**: OpenAPI spec with examples
6. **Migration plan**: Phased rollout strategy
7. **Versioning**: API version strategy

## Standard Response Envelope

```typescript
// types/api-contract.ts
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: ApiError;
  meta?: ResponseMeta;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, string[] | string>;
  trace_id?: string;
}

export interface ResponseMeta {
  timestamp: string;
  request_id: string;
  version: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  meta: ResponseMeta & PaginationMeta;
}

export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}
```

## Pagination Standards

```typescript
// Standard pagination query params
interface PaginationQuery {
  page: number;      // 1-indexed, default: 1
  limit: number;     // default: 10, max: 100
  sort_by?: string;  // field name
  sort_order?: 'asc' | 'desc'; // default: 'desc'
}

// Standard pagination response
{
  "success": true,
  "data": [...],
  "meta": {
    "page": 1,
    "limit": 10,
    "total": 156,
    "total_pages": 16,
    "has_next": true,
    "has_prev": false
  }
}

// Cursor-based pagination (for large datasets)
interface CursorPaginationQuery {
  cursor?: string;
  limit: number;
}

interface CursorPaginationMeta {
  next_cursor?: string;
  prev_cursor?: string;
  has_more: boolean;
}
```

## Best Practices

1. **Consistent envelope**: All responses use same structure
2. **Type safety**: Shared types across frontend/backend
3. **Clear errors**: Descriptive codes and messages
4. **Standard pagination**: Same format for all lists
5. **Versioning**: Plan for API evolution
6. **Documentation**: OpenAPI spec as source of truth
7. **Gradual migration**: Don't break existing clients
8. **Monitoring**: Track adoption and errors

## Output Checklist

- [ ] Standard response envelope defined
- [ ] Error taxonomy documented
- [ ] Pagination format standardized
- [ ] Status code mapping
- [ ] Normalization middleware
- [ ] Shared TypeScript types
- [ ] Versioning strategy
- [ ] OpenAPI specification
- [ ] Migration plan with phases
- [ ] Consumer communication plan


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

