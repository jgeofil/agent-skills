# GitHub Actions Pipeline Creator - Implementation Guide & Code Recipes

## Advanced Caching

```yaml
- name: Cache dependencies
  uses: actions/cache@v3
  with:
    path: |
      ~/.npm
      node_modules
      .next/cache
    key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-npm-

- name: Cache build
  uses: actions/cache@v3
  with:
    path: |
      dist
      .cache
    key: build-${{ github.sha }}
    restore-keys: |
      build-
```

## Docker Build & Push

```yaml
docker:
  name: Build & Push Docker
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Login to Docker Hub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: mycompany/myapp
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=sha

    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=registry,ref=mycompany/myapp:buildcache
        cache-to: type=registry,ref=mycompany/myapp:buildcache,mode=max
```

## Deployment Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: "Environment to deploy to"
        required: true
        type: choice
        options:
          - staging
          - production

jobs:
  deploy:
    name: Deploy to ${{ github.event.inputs.environment || 'staging' }}
    runs-on: ubuntu-latest
    environment:
      name: ${{ github.event.inputs.environment || 'staging' }}
      url: https://${{ steps.deploy.outputs.url }}

    steps:
      - uses: actions/checkout@v4

      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/

      - name: Deploy to Vercel
        id: deploy
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: ${{ github.event.inputs.environment == 'production' && '--prod' || '' }}
```

## Failure Diagnostics

```yaml
- name: Run tests
  id: test
  run: npm test
  continue-on-error: true

- name: Upload test results
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: test-results
    path: |
      test-results/
      coverage/

- name: Comment PR with results
  if: failure() && github.event_name == 'pull_request'
  uses: actions/github-script@v7
  with:
    script: |
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: '❌ Tests failed. Check the [test results](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})'
      })

- name: Fail if tests failed
  if: steps.test.outcome == 'failure'
  run: exit 1
```

## Composite Actions

```yaml
# .github/actions/setup-node/action.yml
name: "Setup Node.js with Cache"
description: "Setup Node.js and restore cache"

inputs:
  node-version:
    description: "Node.js version"
    required: false
    default: "20"

runs:
  using: "composite"
  steps:
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
        cache: "npm"

    - name: Install dependencies
      shell: bash
      run: npm ci
# Usage in workflow:
# - uses: ./.github/actions/setup-node
#   with:
#     node-version: '20'
```

## Conditional Jobs

```yaml
lint:
  if: github.event_name == 'pull_request'
  runs-on: ubuntu-latest
  steps: [...]

deploy:
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  needs: [build, test]
  runs-on: ubuntu-latest
  steps: [...]
```
