---
name: github-actions-pipeline-creator
description: >-
  Creates comprehensive GitHub Actions CI/CD workflows for linting, testing, building, and deploying. Includes caching strategies, matrix builds, artifact handling, and failure diagnostics. Use for "GitHub Actions", "CI pipeline", "workflow automation", or "continuous integration".
license: MIT
metadata:
  version: "1.0"
  category: ci-cd-swe
---

# GitHub Actions Pipeline Creator

Build production-ready GitHub Actions workflows with best practices.

## Basic CI Workflow

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

# Cancel in-progress runs for same workflow
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Run ESLint
        run: npm run lint

      - name: Run Prettier
        run: npm run format:check

      - name: Run TypeScript
        run: npm run type-check

  test:
    name: Test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json
          flags: unittests
          fail_ci_if_error: true

  build:
    name: Build
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build
        env:
          NODE_ENV: production

      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
          retention-days: 7
```

## Matrix Strategy

```yaml
test:
  name: Test
  runs-on: ${{ matrix.os }}
  strategy:
    matrix:
      os: [ubuntu-latest, macos-latest, windows-latest]
      node-version: [18, 20, 21]
      exclude:
        # Skip Windows + Node 18 (slow)
        - os: windows-latest
          node-version: 18
    fail-fast: false

  steps:
    - uses: actions/checkout@v4

    - name: Setup Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
        cache: "npm"

    - run: npm ci
    - run: npm test
```

## Best Practices

1. **Cache dependencies**: Speeds up 3-5x
2. **Parallel jobs**: Run lint/test/build concurrently
3. **Matrix strategy**: Test multiple versions/platforms
4. **Fail fast**: Stop on first failure (or not)
5. **Upload artifacts**: Debug failures
6. **Concurrency control**: Cancel outdated runs
7. **Secrets management**: Never log secrets
8. **Status checks**: Require passing CI

## Output Checklist

- [ ] Lint job configured
- [ ] Test job with coverage
- [ ] Build job with artifacts
- [ ] Deploy job with environments
- [ ] Caching strategy implemented
- [ ] Matrix builds (if needed)
- [ ] Failure diagnostics
- [ ] PR comments on failure
- [ ] Docker build (if needed)
- [ ] Status badges in README


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

