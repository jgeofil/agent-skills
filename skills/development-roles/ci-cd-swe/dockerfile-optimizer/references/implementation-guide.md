# Dockerfile Optimizer - Implementation Guide & Code Recipes

## Layer Caching Optimization

### Order Instructions by Change Frequency

```dockerfile
# ✓ GOOD: Least changing → Most changing
FROM node:20-alpine

# 1. System dependencies (rarely change)
RUN apk add --no-cache dumb-init

# 2. Create user (rarely changes)
RUN adduser -D appuser

# 3. Set working directory
WORKDIR /app

# 4. Copy dependency files (change occasionally)
COPY package.json package-lock.json ./

# 5. Install dependencies (cached if package files unchanged)
RUN npm ci --production

# 6. Copy source code (changes frequently)
COPY --chown=appuser:appuser . .

USER appuser
CMD ["dumb-init", "node", "index.js"]
```

```dockerfile
# ✗ BAD: Source code before dependencies
FROM node:20-alpine
WORKDIR /app
COPY . .                    # Invalidates cache on ANY file change
RUN npm install             # Must reinstall every time
CMD ["node", "index.js"]
```

### .dockerignore

```dockerignore
# Version control
.git
.gitignore

# Dependencies (reinstalled in container)
node_modules
.pnpm-store

# Build outputs
dist
build
.next
out

# Development files
.env*.local
*.log
coverage
.nyc_output

# IDE
.idea
.vscode
*.swp
*.swo

# Docker
Dockerfile*
docker-compose*
.docker

# Documentation
*.md
docs

# Tests (unless needed in container)
__tests__
*.test.ts
*.spec.ts
jest.config.*
```

## Image Size Reduction

### Clean Up in Same Layer

```dockerfile
# ✓ GOOD: Install and clean in one layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# ✗ BAD: Separate layers (cleanup doesn't reduce size)
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*  # Too late, already in previous layer
```

### Use --no-install-recommends

```dockerfile
# ✓ Minimal installation
RUN apt-get install -y --no-install-recommends package-name

# ✗ Installs unnecessary recommended packages
RUN apt-get install -y package-name
```

### Alpine Package Management

```dockerfile
# Alpine uses apk, not apt
RUN apk add --no-cache \
    curl \
    git \
    && rm -rf /var/cache/apk/*
```

## Security Hardening

### Non-Root User

```dockerfile
# Create user in Debian/Ubuntu
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Create user in Alpine
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Set ownership and switch user
COPY --chown=appuser:appgroup . .
USER appuser
```

### Read-Only Filesystem

```dockerfile
# In docker-compose.yml or docker run
services:
  app:
    read_only: true
    tmpfs:
      - /tmp
      - /var/run
```

### Security Scanning

```dockerfile
# Add labels for security scanning
LABEL org.opencontainers.image.source="https://github.com/org/repo"
LABEL org.opencontainers.image.description="Application description"
LABEL org.opencontainers.image.licenses="MIT"
```

### Minimal Capabilities

```yaml
# docker-compose.yml
services:
  app:
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE  # Only if binding to port < 1024
    security_opt:
      - no-new-privileges:true
```

## Health Checks

### HTTP Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1
```

### Without curl (smaller image)

```dockerfile
# Node.js
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

# Python
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# wget (Alpine)
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1
```

## Environment Variables

```dockerfile
# Build-time arguments
ARG NODE_ENV=production
ARG APP_VERSION=unknown

# Runtime environment variables
ENV NODE_ENV=$NODE_ENV
ENV APP_VERSION=$APP_VERSION

# Don't include secrets in Dockerfile
# Use docker run --env-file or secrets management
```

## Docker Compose for Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: development  # Multi-stage target
    volumes:
      - .:/app
      - /app/node_modules  # Anonymous volume for node_modules
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
    command: npm run dev

  app-prod:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    healthcheck:
      test: ["CMD", "wget", "--spider", "http://localhost:3000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
```

## CI/CD Integration

### GitHub Actions Build

```yaml
# .github/workflows/docker.yml
name: Docker Build

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Scan for vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/${{ github.repository }}:${{ github.sha }}
          format: 'table'
          exit-code: '1'
          severity: 'CRITICAL,HIGH'
```

## Common Optimizations

### Pin Versions

```dockerfile
# ✓ Pinned versions for reproducibility
FROM node:20.11.0-alpine3.19

# ✗ Latest tags can break builds
FROM node:latest
FROM node:20-alpine
```

### Use COPY Instead of ADD

```dockerfile
# ✓ COPY is explicit and preferred
COPY package.json .

# ✗ ADD has extra features rarely needed
ADD package.json .  # Only use for URLs or tar extraction
```

### Combine RUN Commands

```dockerfile
# ✓ Single layer, smaller image
RUN apt-get update && \
    apt-get install -y package1 package2 && \
    rm -rf /var/lib/apt/lists/*

# ✗ Multiple layers, larger image
RUN apt-get update
RUN apt-get install -y package1
RUN apt-get install -y package2
```

## Debugging

### Inspect Image Layers

```bash
# View layer history
docker history image-name

# Analyze image with dive
docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  wagoodman/dive:latest image-name
```

### Build with Progress

```bash
# Detailed build output
docker build --progress=plain -t myapp .

# Build specific stage
docker build --target builder -t myapp:builder .
```
