# Git Hygiene Enforcer - Implementation Guide & Code Recipes

## Branch Naming Conventions

**Pattern:** `<type>/<ticket-id>-<description>`

**Examples:**

```
feature/AUTH-123-oauth-login
bugfix/API-456-user-race-condition
hotfix/PROD-789-payment-error
refactor/DB-321-optimize-queries
```

**Branch Protection Rules:**

- Require PR reviews (1-2 reviewers)
- Require status checks to pass
- Require branches to be up to date
- Enforce linear history (no merge commits)
- Require signed commits (optional)

## Pull Request Templates

### .github/pull_request_template.md

```markdown
## Description

<!-- Describe your changes in detail -->

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Related Issue

Closes #<!-- issue number -->

## How Has This Been Tested?

<!-- Describe the tests you ran to verify your changes -->

- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing
