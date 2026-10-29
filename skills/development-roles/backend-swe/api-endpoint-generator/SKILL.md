---
name: api-endpoint-generator
description: >-
  Generates CRUD REST API endpoints with request validation, TypeScript types, consistent response formats, error handling, and documentation. Includes route handlers, validation schemas (Zod/Joi), typed responses, and usage examples. Use when building "REST API", "CRUD endpoints", "API routes", or "backend endpoints".
license: MIT
metadata:
  version: "1.0"
  category: backend-swe
---

# API Endpoint Generator

Generate production-ready CRUD API endpoints with validation and type safety.

## Core Workflow

1. **Define resource**: Entity name and schema
2. **Generate routes**: POST, GET, PUT/PATCH, DELETE endpoints
3. **Add validation**: Request body/query validation with Zod/Joi
4. **Type responses**: TypeScript interfaces for all responses
5. **Error handling**: Consistent error responses
6. **Documentation**: OpenAPI/Swagger specs
7. **Examples**: Request/response samples

## Express + TypeScript Pattern

```typescript
// types/user.types.ts
export interface User {
  id: string;
  email: string;
  name: string;
  role: "user" | "admin";
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateUserDto {
  email: string;
  name: string;
  password: string;
}

export interface UpdateUserDto {
  name?: string;
  email?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ApiError;
  meta?: PaginationMeta;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, string[]>;
}
```

## Validation Schemas (Zod)

```typescript
// schemas/user.schema.ts
import { z } from "zod";

export const createUserSchema = z.object({
  email: z.string().email("Invalid email address"),
  name: z.string().min(2, "Name must be at least 2 characters"),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .regex(/[A-Z]/, "Password must contain uppercase letter")
    .regex(/[0-9]/, "Password must contain number"),
});

export const updateUserSchema = z
  .object({
    name: z.string().min(2).optional(),
    email: z.string().email().optional(),
  })
  .refine((data) => Object.keys(data).length > 0, {
    message: "At least one field must be provided",
  });

export const getUsersQuerySchema = z.object({
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().min(1).max(100).default(10),
  sortBy: z.enum(["name", "email", "createdAt"]).optional(),
  sortOrder: z.enum(["asc", "desc"]).default("desc"),
  search: z.string().optional(),
});

export type CreateUserDto = z.infer<typeof createUserSchema>;
export type UpdateUserDto = z.infer<typeof updateUserSchema>;
export type GetUsersQuery = z.infer<typeof getUsersQuerySchema>;
```

## Best Practices

1. **Type everything**: Request, response, DTOs, errors
2. **Validate early**: Before hitting service layer
3. **Consistent responses**: Same structure everywhere
4. **HTTP semantics**: Use correct status codes
5. **Error details**: Include validation errors
6. **Pagination**: Always paginate lists
7. **Filtering/sorting**: Support common queries
8. **Documentation**: OpenAPI/Swagger specs

## Output Checklist

- [ ] Route definitions with HTTP methods
- [ ] Request validation schemas
- [ ] TypeScript types for all DTOs
- [ ] Controller handlers with error handling
- [ ] Consistent response format
- [ ] Pagination for list endpoints
- [ ] HTTP status codes correctly used
- [ ] Error response format
- [ ] OpenAPI/Swagger documentation
- [ ] Usage examples with curl/requests


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

