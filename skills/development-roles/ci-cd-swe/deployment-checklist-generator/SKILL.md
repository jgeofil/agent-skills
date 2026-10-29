---
name: deployment-checklist-generator
description: >-
  Creates comprehensive deployment checklists with pre-deployment checks, smoke tests, verification steps, and sign-off workflows. Use for "deployment checklist", "release verification", "deployment runbook", or "production readiness".
license: MIT
metadata:
  version: "1.0"
  category: ci-cd-swe
---

# Deployment Checklist Generator

Ensure safe, reliable deployments with comprehensive checklists.

## Pre-Deployment Checklist

```markdown
# Pre-Deployment Checklist

## Code Quality

- [ ] All CI checks passing
- [ ] Code review approved (2+ reviewers)
- [ ] No known critical bugs
- [ ] Security scan passed
- [ ] Performance tests passed

## Dependencies

- [ ] All dependencies up to date
- [ ] No high/critical vulnerabilities
- [ ] Bundle size within budget
- [ ] Third-party services operational

## Database

- [ ] Migrations tested in staging
- [ ] Backup completed
- [ ] Rollback plan documented
- [ ] Data migration scripts reviewed

## Infrastructure

- [ ] Servers have capacity
- [ ] CDN cache invalidation plan
- [ ] Load balancer configured
- [ ] SSL certificates valid

## Documentation

- [ ] Changelog updated
- [ ] API docs updated (if changed)
- [ ] Deployment notes prepared
- [ ] Rollback instructions ready

## Communication

- [ ] Stakeholders notified
- [ ] Maintenance window scheduled (if needed)
- [ ] Support team briefed
- [ ] Status page prepared

## Deployment Window

- [ ] Off-peak hours selected
- [ ] Team available for monitoring
- [ ] Emergency contacts confirmed
```

## Deployment Workflow with Checks

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  workflow_dispatch:

jobs:
  pre-deploy-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check branch
        run: |
          if [ "${{ github.ref }}" != "refs/heads/main" ]; then
            echo "❌ Can only deploy from main branch"
            exit 1
          fi

      - name: Verify CI passed
        uses: actions/github-script@v7
        with:
          script: |
            const checks = await github.rest.checks.listForRef({
              owner: context.repo.owner,
              repo: context.repo.repo,
              ref: context.sha,
            });

            const failed = checks.data.check_runs.filter(
              check => check.conclusion === 'failure'
            );

            if (failed.length > 0) {
              throw new Error(`CI checks failed: ${failed.map(c => c.name).join(', ')}`);
            }

      - name: Check deployment window
        run: |
          HOUR=$(date +%H)
          if [ $HOUR -ge 9 ] && [ $HOUR -le 17 ]; then
            echo "⚠️ Deploying during business hours"
          else
            echo "✅ Deploying outside business hours"
          fi

      - name: Verify staging deployment
        run: |
          if ! curl -f https://staging.myapp.com/health; then
            echo "❌ Staging is not healthy"
            exit 1
          fi

  deploy:
    needs: pre-deploy-checks
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://myapp.com
    steps:
      - uses: actions/checkout@v4

      - name: Backup database
        run: ./scripts/backup-db.sh

      - name: Deploy
        run: ./scripts/deploy.sh production

      - name: Run smoke tests
        run: ./scripts/smoke-tests.sh production

      - name: Update status page
        run: |
          curl -X POST https://statuspage.io/api/v1/incidents \
            -H "Authorization: Bearer ${{ secrets.STATUSPAGE_TOKEN }}" \
            -d '{"name":"Deployment Complete","status":"resolved"}'

      - name: Create deployment record
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.repos.createDeployment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              ref: context.sha,
              environment: 'production',
              description: 'Production deployment',
            });
```


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

