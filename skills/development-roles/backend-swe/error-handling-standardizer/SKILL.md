---
name: error-handling-standardizer
description: >-
  Creates consistent error handling with custom error classes, HTTP status mapping, structured logging, safe client messages, and error taxonomy. Use when standardizing "error handling", "logging", "error responses", or "exception management".
license: MIT
metadata:
  version: "1.0"
  category: backend-swe
---

# Error Handling Standardizer

Build consistent, debuggable error handling across the application.

## Error Taxonomy

```typescript
export class AppError extends Error {
  constructor(
    public code: string,
    public message: string,
    public statusCode: number = 500,
    public isOperational: boolean = true,
    public details?: any
  ) {
    super(message);
    Error.captureStackTrace(this, this.constructor);
  }
}

export class ValidationError extends AppError {
  constructor(details: Record<string, string[]>) {
    super("VALIDATION_ERROR", "Validation failed", 400, true, details);
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string) {
    super("NOT_FOUND", `${resource} not found`, 404);
  }
}

export class UnauthorizedError extends AppError {
  constructor(message = "Unauthorized") {
    super("UNAUTHORIZED", message, 401);
  }
}

export class ForbiddenError extends AppError {
  constructor(message = "Forbidden") {
    super("FORBIDDEN", message, 403);
  }
}
```

## Error Handler Middleware

```typescript
export const errorHandler = (
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  // Log error
  logger.error("Request error", {
    error: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method,
    requestId: req.id,
  });

  // Operational errors (known)
  if (err instanceof AppError && err.isOperational) {
    return res.status(err.statusCode).json({
      success: false,
      error: {
        code: err.code,
        message: err.message,
        details: err.details,
        trace_id: req.id,
      },
    });
  }

  // Programming errors (unknown)
  return res.status(500).json({
    success: false,
    error: {
      code: "INTERNAL_ERROR",
      message: "An unexpected error occurred",
      trace_id: req.id,
    },
  });
};
```

## Structured Logging

```typescript
import winston from "winston";

export const logger = winston.createLogger({
  level: "info",
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: "error.log", level: "error" }),
    new winston.transports.File({ filename: "combined.log" }),
  ],
});

// Log with context
logger.error("Payment processing failed", {
  userId: user.id,
  amount: payment.amount,
  error: err.message,
  trace_id: req.id,
});
```

## Safe Client Messages

```typescript
// Never expose internal errors to clients
const getSafeErrorMessage = (err: Error): string => {
  if (err instanceof AppError && err.isOperational) {
    return err.message; // Safe, user-facing message
  }

  // Generic message for unexpected errors
  return "An unexpected error occurred";
};
```

## Async Error Handling

```typescript
// Wrap async routes
export const asyncHandler = (fn: RequestHandler) => {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};

// Usage
router.get(
  "/users",
  asyncHandler(async (req, res) => {
    const users = await userService.findAll();
    res.json(users);
  })
);
```

## Best Practices

- Use custom error classes
- Distinguish operational vs programming errors
- Log all errors with context
- Never expose stack traces to clients
- Include trace IDs for debugging
- Monitor error rates by type
- Set up alerting for critical errors

## Output Checklist

- [ ] Custom error classes defined
- [ ] Error handler middleware
- [ ] HTTP status code mapping
- [ ] Structured logging setup
- [ ] Safe client error messages
- [ ] Async error wrapper
- [ ] Error monitoring/alerts
- [ ] Documentation of error codes

## Discriminated Unions & Result Types (Spec-First Alignment)

> [!TIP]
> In **Spec-First Architectures (`spec-first-architect-v2`)** and pure domain / adapter boundaries, prefer explicit **Discriminated Union Return Types** over thrown exceptions:
> ```typescript
> export type AdapterResult<T, E = AdapterError> =
>   | { ok: true; value: T }
>   | { ok: false; error: E };
> ```
> Adapters must catch all upstream HTTP/transport errors (`429`, timeouts) and map them into the discriminated union. This prevents raw runtime exceptions from leaking into domain cells and makes error states exhaustively verifiable in black-box contract tests.

## Related Skills

- `spec-first-architect-v2` — Enforces total error mapping into discriminated unions across Layer 1 contracts and adapter cells
- `api-contract-normalizer` — Consistent response and error envelopes
- `python-error-handling` — Python-specific exception hierarchies and error handling patterns
