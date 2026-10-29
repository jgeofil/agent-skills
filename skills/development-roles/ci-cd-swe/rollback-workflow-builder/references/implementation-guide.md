# Rollback Workflow Builder - Implementation Guide & Code Recipes

## Kubernetes Rollback

```yaml
rollback-k8s:
  runs-on: ubuntu-latest
  steps:
    - name: Setup kubectl
      uses: azure/setup-kubectl@v3

    - name: Configure kubectl
      run: |
        echo "${{ secrets.KUBECONFIG }}" > kubeconfig
        export KUBECONFIG=kubeconfig

    - name: Rollback deployment
      run: |
        kubectl rollout undo deployment/myapp -n production
        kubectl rollout status deployment/myapp -n production --timeout=5m

    - name: Get rollback revision
      run: |
        kubectl rollout history deployment/myapp -n production
```

## Docker Image Rollback

```yaml
- name: Rollback to previous image
  run: |
    # Get previous image tag
    PREVIOUS_TAG=$(docker inspect myapp:latest | jq -r '.[0].ContainerConfig.Labels.previous_tag')

    # Retag previous as latest
    docker pull myapp:$PREVIOUS_TAG
    docker tag myapp:$PREVIOUS_TAG myapp:latest
    docker push myapp:latest

    # Restart containers
    docker-compose pull
    docker-compose up -d
```

## Database Migration Rollback

```yaml
- name: Rollback database migrations
  run: |
    # Get migration to rollback to
    CURRENT=$(npm run migrate:current)
    TARGET=${{ github.event.inputs.migration }}

    echo "Rolling back from $CURRENT to $TARGET"
    npm run migrate:down -- --to=$TARGET

    # Verify rollback
    AFTER=$(npm run migrate:current)
    if [ "$AFTER" != "$TARGET" ]; then
      echo "❌ Migration rollback failed"
      exit 1
    fi
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

## Rollback Runbook

````markdown
# Production Rollback Runbook

## When to Rollback

Rollback if:

- Critical bugs affecting >10% of users
- Data integrity issues
- Security vulnerabilities
- Performance degradation >50%
- Error rate >5%

## Before Rollback

1. **Assess impact**: Check monitoring dashboards
2. **Identify version**: Determine last known good version
3. **Notify team**: Post in #incidents Slack channel
4. **Enable maintenance mode** (if possible)

## Rollback Steps

### Automated Rollback (Preferred)

1. Go to Actions → Rollback workflow
2. Select environment (staging/production)
3. Enter target version (e.g., v1.2.3 or "previous")
4. Enter reason for rollback
5. Click "Run workflow"
6. Monitor progress in Actions tab

### Manual Rollback (Emergency)

```bash
# 1. SSH to production server
ssh production

# 2. Check current version
docker ps | grep myapp

# 3. Pull previous version
docker pull myapp:v1.2.3

# 4. Update docker-compose
vim docker-compose.yml
# Change image: myapp:latest to myapp:v1.2.3

# 5. Deploy
docker-compose up -d

# 6. Verify
curl https://api.myapp.com/health

# 7. Check logs
docker logs myapp -f
```
````

## After Rollback

1. **Verify**: Run smoke tests
2. **Monitor**: Watch error rates for 15 minutes
3. **Notify**: Update #incidents with status
4. **Disable maintenance mode**
5. **Create incident ticket**
6. **Schedule postmortem**

## Rollback Verification

- [ ] Health check returns 200
- [ ] Error rate <1%
- [ ] Response time p95 <500ms
- [ ] Key features working (login, checkout, etc.)
- [ ] Database connectivity OK

## Communication Template

```
🔄 ROLLBACK IN PROGRESS

Environment: Production
From: v1.3.0
To: v1.2.3
Reason: Critical bug in checkout flow
Status: In progress
ETA: 5 minutes

Updates: #incidents
```

## Common Issues

### Issue: Rollback Fails

**Symptom:** Deployment doesn't start
**Fix:** Check logs, verify version exists, ensure secrets are valid

### Issue: Database Incompatibility

**Symptom:** App starts but can't read data
**Fix:** May need to rollback migrations first

### Issue: Traffic Not Routing

**Symptom:** Users still see new version
**Fix:** Clear CDN cache, check load balancer config

````

## Health Check Script

```bash
#!/bin/bash
# scripts/health-check.sh

ENVIRONMENT=$1
BASE_URL="https://${ENVIRONMENT}.myapp.com"

echo "Running health checks for $ENVIRONMENT..."

# API health
if ! curl -f "$BASE_URL/api/health" > /dev/null 2>&1; then
  echo "❌ API health check failed"
  exit 1
fi

# Database connection
if ! curl -f "$BASE_URL/api/health/db" > /dev/null 2>&1; then
  echo "❌ Database health check failed"
  exit 1
fi

# Key endpoints
ENDPOINTS=("/api/users" "/api/products" "/api/orders")
for endpoint in "${ENDPOINTS[@]}"; do
  if ! curl -f "$BASE_URL$endpoint" > /dev/null 2>&1; then
    echo "❌ Endpoint $endpoint health check failed"
    exit 1
  fi
done

echo "✅ All health checks passed"
exit 0
````
