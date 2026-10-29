---
name: rollback-workflow-builder
description: >-
  Creates safe rollback procedures for deployments with automated workflows, rollback runbooks, version management, and incident response. Use for "rollback automation", "deployment recovery", "incident response", or "production rollback".
license: MIT
metadata:
  version: "1.0"
  category: ci-cd-swe
---

# Rollback Workflow Builder

Build safe, fast rollback mechanisms for production deployments.

## Manual Rollback Workflow

```yaml
# .github/workflows/rollback.yml
name: Rollback

on:
  workflow_dispatch:
    inputs:
      version:
        description: "Version to rollback to (e.g., v1.2.3 or previous)"
        required: true
        type: string
      environment:
        description: "Environment to rollback"
        required: true
        type: choice
        options:
          - staging
          - production
      reason:
        description: "Reason for rollback"
        required: true
        type: string

jobs:
  rollback:
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment }}
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.inputs.version }}

      - name: Verify version exists
        run: |
          if ! git rev-parse ${{ github.event.inputs.version }} >/dev/null 2>&1; then
            echo "❌ Version ${{ github.event.inputs.version }} not found"
            exit 1
          fi
          echo "✅ Version ${{ github.event.inputs.version }} exists"

      - name: Get current version
        id: current
        run: |
          CURRENT=$(git describe --tags --abbrev=0)
          echo "version=$CURRENT" >> $GITHUB_OUTPUT
          echo "Current version: $CURRENT"

      - name: Confirm rollback
        run: |
          echo "🔄 Rolling back from ${{ steps.current.outputs.version }} to ${{ github.event.inputs.version }}"
          echo "Environment: ${{ github.event.inputs.environment }}"
          echo "Reason: ${{ github.event.inputs.reason }}"

      - uses: actions/setup-node@v4
        with:
          node-version: "20"

      - run: npm ci
      - run: npm run build

      - name: Deploy rollback
        run: |
          ./scripts/deploy.sh ${{ github.event.inputs.environment }}
        env:
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}

      - name: Verify deployment
        run: |
          ./scripts/health-check.sh ${{ github.event.inputs.environment }}

      - name: Create incident issue
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `Rollback: ${context.payload.inputs.environment} to ${context.payload.inputs.version}`,
              body: `## Rollback Details

              **Environment:** ${context.payload.inputs.environment}
              **From:** ${{ steps.current.outputs.version }}
              **To:** ${context.payload.inputs.version}
              **Reason:** ${context.payload.inputs.reason}
              **Triggered by:** @${context.actor}
              **Time:** ${new Date().toISOString()}

              ## Next Steps
              - [ ] Verify rollback successful
              - [ ] Investigate root cause
              - [ ] Create fix
              - [ ] Update postmortem
              `,
              labels: ['incident', 'rollback']
            })
```

## Automated Rollback on Failure

```yaml
deploy:
  runs-on: ubuntu-latest
  steps:
    - name: Deploy
      id: deploy
      run: ./scripts/deploy.sh production
      continue-on-error: true

    - name: Verify deployment
      id: verify
      if: steps.deploy.outcome == 'success'
      run: ./scripts/health-check.sh production
      continue-on-error: true

    - name: Auto-rollback on failure
      if: steps.deploy.outcome == 'failure' || steps.verify.outcome == 'failure'
      run: |
        echo "⚠️ Deployment failed, initiating automatic rollback"
        PREVIOUS_VERSION=$(git describe --tags --abbrev=0 HEAD^)
        ./scripts/deploy.sh production $PREVIOUS_VERSION

        # Verify rollback
        if ./scripts/health-check.sh production; then
          echo "✅ Rollback successful"
        else
          echo "❌ Rollback failed - manual intervention required"
          exit 1
        fi
```

## Best Practices

1. **Fast rollback**: <5 minutes to previous version
2. **Automated**: One-click rollback workflow
3. **Verified**: Health checks after rollback
4. **Documented**: Clear runbook
5. **Tested**: Practice rollbacks regularly
6. **Monitored**: Alert on failures
7. **Communicated**: Notify stakeholders

## Output Checklist

- [ ] Manual rollback workflow
- [ ] Automated rollback on failure
- [ ] Platform-specific rollback (K8s/Docker)
- [ ] Database rollback procedure
- [ ] Rollback runbook documented
- [ ] Health check scripts
- [ ] Communication templates
- [ ] Incident issue automation


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

