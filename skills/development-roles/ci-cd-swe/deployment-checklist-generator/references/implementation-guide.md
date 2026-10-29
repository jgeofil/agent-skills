# Deployment Checklist Generator - Implementation Guide & Code Recipes

## Smoke Test Script

```bash
#!/bin/bash
# scripts/smoke-tests.sh

ENVIRONMENT=$1
BASE_URL="https://${ENVIRONMENT}.myapp.com"

echo "🔍 Running smoke tests for $ENVIRONMENT..."

FAILED=0

# Test 1: Health endpoint
echo "Test 1: Health check"
if curl -f "$BASE_URL/health" | grep -q "ok"; then
  echo "✅ Health check passed"
else
  echo "❌ Health check failed"
  FAILED=1
fi

# Test 2: User authentication
echo "Test 2: User login"
TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' \
  | jq -r '.token')

if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
  echo "✅ Login passed"
else
  echo "❌ Login failed"
  FAILED=1
fi

# Test 3: Critical API endpoints
echo "Test 3: API endpoints"
ENDPOINTS=("/api/users" "/api/products" "/api/orders")

for endpoint in "${ENDPOINTS[@]}"; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    "$BASE_URL$endpoint")

  if [ "$STATUS" == "200" ]; then
    echo "✅ $endpoint: $STATUS"
  else
    echo "❌ $endpoint: $STATUS"
    FAILED=1
  fi
done

# Test 4: Database connectivity
echo "Test 4: Database check"
if curl -f "$BASE_URL/api/health/db" | grep -q "connected"; then
  echo "✅ Database connected"
else
  echo "❌ Database connection failed"
  FAILED=1
fi

# Test 5: External services
echo "Test 5: External services"
SERVICES=("stripe" "sendgrid" "aws")

for service in "${SERVICES[@]}"; do
  if curl -f "$BASE_URL/api/health/$service" | grep -q "ok"; then
    echo "✅ $service: connected"
  else
    echo "❌ $service: connection failed"
    FAILED=1
  fi
done

if [ $FAILED -eq 1 ]; then
  echo "❌ Smoke tests failed"
  exit 1
fi

echo "✅ All smoke tests passed"
exit 0
```

## Post-Deployment Verification

```markdown
# Post-Deployment Verification

## Immediate Checks (0-5 minutes)

- [ ] Deployment completed successfully
- [ ] All smoke tests passed
- [ ] Health checks returning 200
- [ ] No 5xx errors in logs
- [ ] Application responding

## Short-term Monitoring (5-30 minutes)

- [ ] Error rate <1%
- [ ] Response time p95 <500ms
- [ ] CPU usage normal (<70%)
- [ ] Memory usage stable
- [ ] Database queries performing well

## Feature Verification

- [ ] Login/authentication working
- [ ] Checkout flow functional
- [ ] Search returning results
- [ ] Email notifications sending
- [ ] Payment processing working

## Metrics Dashboard

- [ ] Request volume normal
- [ ] Success rate >99%
- [ ] Latency within SLA
- [ ] No spike in errors
- [ ] User engagement stable

## Long-term Monitoring (1-24 hours)

- [ ] No user complaints
- [ ] Support tickets normal
- [ ] Revenue tracking normal
- [ ] All scheduled jobs running
- [ ] No memory leaks detected
```

## Sign-off Template

```yaml
- name: Request deployment approval
  uses: trstringer/manual-approval@v1
  with:
    secret: ${{ secrets.GITHUB_TOKEN }}
    approvers: tech-lead,ops-manager
    minimum-approvals: 2
    issue-title: "Approve Production Deployment"
    issue-body: |
      ## Deployment Details

      **Version:** ${{ github.ref_name }}
      **Commit:** ${{ github.sha }}
      **Changes:** See [changelog](CHANGELOG.md)

      ## Pre-deployment Checklist
      - ✅ All CI checks passed
      - ✅ Code review completed
      - ✅ Security scan passed
      - ✅ Staging verified

      ## Approval Required
      This deployment requires approval from tech lead and ops manager.

      **Approve:** Comment "approve" or "lgtm"
      **Reject:** Comment "reject" or "block"
```

## Monitoring Dashboard

```markdown
# Deployment Monitoring Dashboard

## Key Metrics

### Health

- API Health: ✅ UP
- Database: ✅ Connected
- Cache: ✅ Connected

### Performance

- Requests/min: 1,234
- Error rate: 0.2%
- p50 latency: 120ms
- p95 latency: 450ms
- p99 latency: 1,200ms

### Infrastructure

- CPU: 45%
- Memory: 62%
- Disk: 38%

### Business Metrics

- Active users: 523
- Successful checkouts: 89/hour
- Revenue: $15,234/hour

## Alerts

No active alerts

## Recent Deployments

- v1.3.0: Deployed 5 minutes ago ✅
- v1.2.9: Deployed 2 days ago ✅
- v1.2.8: Rolled back 3 days ago ⚠️
```

## Best Practices

1. **Automated checks**: Enforce via CI/CD
2. **Manual review**: Critical deployments need approval
3. **Smoke tests**: Verify key functionality
4. **Gradual rollout**: Canary or blue-green
5. **Monitoring**: Watch metrics for 30 minutes
6. **Communication**: Keep stakeholders informed
7. **Rollback ready**: One-click rollback available

## Output Checklist

- [ ] Pre-deployment checklist
- [ ] Deployment workflow with gates
- [ ] Smoke test script
- [ ] Post-deployment verification
- [ ] Sign-off workflow
- [ ] Monitoring dashboard
- [ ] Communication templates
- [ ] Rollback instructions
