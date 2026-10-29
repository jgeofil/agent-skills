---
name: dockerfile-optimizer
description: >-
  Optimizes Dockerfiles for smaller images, faster builds, better caching, and security hardening using multi-stage builds and best practices. Use when users request "optimize Dockerfile", "reduce Docker image size", "Docker best practices", or "containerize application".
license: MIT
metadata:
  version: "1.0"
  category: ci-cd-swe
---

# Dockerfile Optimizer

Build optimized, secure, and cache-efficient Docker images following production best practices.

## Core Workflow

1. **Analyze current Dockerfile**: Identify optimization opportunities
2. **Implement multi-stage builds**: Separate build and runtime
3. **Optimize layer caching**: Order instructions efficiently
4. **Minimize image size**: Use slim base images and cleanup
5. **Add security hardening**: Non-root user, minimal permissions
6. **Configure health checks**: Ensure container health monitoring

## Base Image Selection

### Image Size Comparison

| Base Image | Size | Use Case |
|------------|------|----------|
| `node:20` | ~1GB | Development only |
| `node:20-slim` | ~200MB | General production |
| `node:20-alpine` | ~130MB | Size-critical production |
| `gcr.io/distroless/nodejs20` | ~120MB | Maximum security |

### Recommendations by Language

```dockerfile
# Node.js
FROM node:20-alpine

# Python
FROM python:3.12-slim

# Go
FROM golang:1.22-alpine AS builder
FROM scratch AS runtime  # Or gcr.io/distroless/static

# Rust
FROM rust:1.75-alpine AS builder
FROM alpine:3.19 AS runtime

# Java
FROM eclipse-temurin:21-jdk-alpine AS builder
FROM eclipse-temurin:21-jre-alpine AS runtime
```

## Multi-Stage Builds

### Node.js Application

```dockerfile
# ==================== Build Stage ====================
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies first (cache layer)
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts

# Copy source and build
COPY . .
RUN npm run build

# Prune dev dependencies
RUN npm prune --production

# ==================== Production Stage ====================
FROM node:20-alpine AS production

# Security: Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

WORKDIR /app

# Copy only necessary files
COPY --from=builder --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nextjs:nodejs /app/dist ./dist
COPY --from=builder --chown=nextjs:nodejs /app/package.json ./

# Security: Switch to non-root user
USER nextjs

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

EXPOSE 3000

CMD ["node", "dist/index.js"]
```

### Next.js Application

```dockerfile
# ==================== Dependencies ====================
FROM node:20-alpine AS deps

RUN apk add --no-cache libc6-compat

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

# ==================== Builder ====================
FROM node:20-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Disable telemetry during build
ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build

# ==================== Runner ====================
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy static assets
COPY --from=builder /app/public ./public

# Set correct permissions for prerender cache
RUN mkdir .next && chown nextjs:nodejs .next

# Copy build output
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || exit 1

CMD ["node", "server.js"]
```

### Python Application

```dockerfile
# ==================== Builder ====================
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ==================== Production ====================
FROM python:3.12-slim AS production

WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Go Application

```dockerfile
# ==================== Builder ====================
FROM golang:1.22-alpine AS builder

RUN apk add --no-cache git ca-certificates tzdata

WORKDIR /app

# Download dependencies
COPY go.mod go.sum ./
RUN go mod download && go mod verify

# Build
COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
    -ldflags="-w -s -X main.version=$(git describe --tags --always)" \
    -o /app/server ./cmd/server

# ==================== Production ====================
FROM scratch AS production

# Copy CA certificates for HTTPS
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /usr/share/zoneinfo /usr/share/zoneinfo

# Copy binary
COPY --from=builder /app/server /server

EXPOSE 8080

ENTRYPOINT ["/server"]
```

## Best Practices

1. **Use multi-stage builds**: Separate build and runtime environments
2. **Order layers by change frequency**: Maximize cache hits
3. **Use .dockerignore**: Exclude unnecessary files
4. **Run as non-root**: Always create and use a non-root user
5. **Pin base image versions**: Ensure reproducible builds
6. **Clean up in same layer**: Reduce image size
7. **Add health checks**: Enable container orchestration
8. **Scan for vulnerabilities**: Use Trivy, Snyk, or similar
9. **Use slim/alpine bases**: Minimize attack surface
10. **Don't store secrets**: Use runtime injection

## Output Checklist

Every optimized Dockerfile should include:

- [ ] Multi-stage build separating build and runtime
- [ ] Slim or Alpine base image
- [ ] Pinned base image version
- [ ] Layer caching optimization (deps before source)
- [ ] Non-root user configuration
- [ ] Health check defined
- [ ] .dockerignore file
- [ ] No secrets in image
- [ ] Minimal installed packages
- [ ] Cleanup in same layer as install
- [ ] Labels for metadata
- [ ] Security scanning in CI


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

