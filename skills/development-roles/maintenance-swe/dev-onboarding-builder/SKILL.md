---
name: dev-onboarding-builder
description: >-
  Creates comprehensive developer onboarding documentation and materials including step-by-step setup guides, first-task assignments, expected time per step, common troubleshooting, team introductions, and code walkthrough tours. Use when preparing "new developer onboarding", "first day setup", "junior dev training", or "team member onboarding".
license: MIT
metadata:
  version: "1.0"
  category: maintenance-swe
---

# Developer Onboarding Builder

Create frictionless first-day experiences for new team members.

## Core Workflow

1. **Assess prerequisites**: Identify required tools and access
2. **Create setup guide**: Step-by-step environment configuration
3. **Design first task**: Choose appropriate starter assignment
4. **Add time estimates**: Set expectations for each step
5. **Document common issues**: Preemptive troubleshooting
6. **Introduce team**: Context on people and structure
7. **Provide codebase tour**: Walkthrough of key areas

## Onboarding Documentation Structure

### ONBOARDING.md Template

````markdown
# Welcome to [Team/Project Name]! 🎉

This guide will help you get set up and productive on your first day.

**Estimated completion time:** 2-3 hours

## Before You Start

### Access Checklist

- [ ] GitHub organization access
- [ ] Slack workspace invitation
- [ ] Email account setup
- [ ] VPN credentials (if remote)
- [ ] Cloud console access (AWS/GCP/Azure)
- [ ] CI/CD dashboard access
- [ ] Project management tool (Jira/Linear)

### Tools to Install

- [ ] Node.js 20+ (via [Volta](https://volta.sh/))
- [ ] pnpm 8+
- [ ] Docker Desktop
- [ ] PostgreSQL 15+
- [ ] VS Code or preferred editor
- [ ] Git configured with your work email

## Day 1: Environment Setup

### Step 1: Clone Repository (5 min)

```bash
git clone git@github.com:company/project-name.git
cd project-name
```
````

**Why:** Get the codebase on your machine

**Troubleshooting:**

- SSH key not working? See [GitHub SSH setup](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- Permission denied? Ask your manager to verify GitHub access

### Step 2: Install Dependencies (10 min)

```bash
# Install Volta (Node version manager)
curl https://get.volta.sh | bash

# Install dependencies
pnpm install
```

**Expected output:** "Dependencies installed successfully"

**Troubleshooting:**

- `pnpm not found`? Restart terminal or run `volta install pnpm`
- Installation hangs? Check VPN connection

### Step 3: Configure Environment (10 min)

```bash
# Copy environment template
cp .env.example .env
```

**Edit `.env` with these values:**

```
DATABASE_URL=postgresql://postgres:password@localhost:5432/projectname_dev
REDIS_URL=redis://localhost:6379
API_KEY=ask-team-for-dev-key
```

**Get credentials from:**

- Database: Local setup (see next step)
- API keys: Ask @alice or @bob on Slack #dev-onboarding
- External services: Check 1Password vault "Dev Credentials"

**Troubleshooting:**

- Can't find credentials? Post in #dev-onboarding
- Missing env var? Check .env.example for all required variables

### Step 4: Setup Database (15 min)

```bash
# Start PostgreSQL with Docker
docker run --name project-postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  -d postgres:15

# Run migrations
pnpm db:migrate

# Seed with test data
pnpm db:seed
```

**Expected output:** "Migration complete. Database seeded."

**Verify:** Open http://localhost:5432 and check for tables

**Troubleshooting:**

- Port 5432 already in use? Kill existing process: `lsof -ti:5432 | xargs kill`
- Migration fails? Drop and recreate: `pnpm db:reset`

### Step 5: Start Development Server (5 min)

```bash
pnpm dev
```

**Expected output:**

```
✓ Ready on http://localhost:3000
```

**Test:** Open http://localhost:3000 - you should see the homepage

**Troubleshooting:**

- Port 3000 in use? Kill process or change PORT in .env
- Build errors? Clear cache: `rm -rf .next && pnpm dev`

### Step 6: Run Tests (5 min)

```bash
pnpm test
```

**Expected output:** All tests passing ✓

**If tests fail:**

- First time? This is a bug! Report in #dev-help
- Known issue? Check #dev-help pinned messages

## Week 1 Checklist

By end of week 1, you should have:

- [ ] Completed environment setup
- [ ] Fixed 2-3 good-first-issues
- [ ] Created first feature PR
- [ ] Met with all team members
- [ ] Attended all team meetings
- [ ] Read key documentation
- [ ] Understood development workflow
- [ ] Know how to get help

## Feedback

We're always improving onboarding! Please share:

- What went well?
- What was confusing?
- What's missing?

**Share in:** #dev-onboarding or with your manager

---

**Welcome to the team! We're excited to have you here! 🚀**

```

## Onboarding Best Practices

### Time Estimates
- Be realistic with timing
- Include buffer for troubleshooting
- Track actual time vs estimated

### Progressive Complexity
- Day 1: Setup and simple task
- Week 1: Understanding patterns
- Month 1: Independent features

### Clear Success Criteria
- Checklist for each step
- Objective completion markers
- Regular check-ins

### Preemptive Troubleshooting
- Document known issues
- Provide solutions upfront
- Update based on new dev feedback

### Human Connection
- Introduce team members
- Schedule 1:1s
- Provide mentors

## First Task Selection Criteria

Good first task should:
- [ ] Be completable in 2-4 hours
- [ ] Touch multiple areas lightly
- [ ] Have clear acceptance criteria
- [ ] Require PR and review
- [ ] Be genuinely useful (not busy work)
- [ ] Have mentor availability

**Examples:**
- Fix typo in error message (touches: frontend, i18n, testing)
- Add validation to API endpoint (touches: backend, testing, docs)
- Improve loading state (touches: frontend, UX, components)

## Documentation Components

### Essential Sections
1. Prerequisites and access
2. Step-by-step setup with time estimates
3. First task assignment
4. Codebase tour
5. Team structure
6. Communication channels
7. Common issues and solutions
8. Resources and next steps

### Optional but Valuable
- Video walkthrough
- Pair programming schedule
- Reading list
- Architecture diagrams
- Glossary of terms

## Maintenance

### Keep Updated
- Review after each new hire
- Update tool versions
- Refresh access instructions
- Add new common issues

### Collect Feedback
- Exit survey after week 1
- Regular check-ins
- Track time to productivity
- Document pain points

## Output Checklist

Complete onboarding package includes:

- [ ] ONBOARDING.md with step-by-step guide
- [ ] Time estimates for each step
- [ ] First task identified and documented
- [ ] Team structure and communication
- [ ] Troubleshooting for common issues
- [ ] Links to all necessary resources
- [ ] Checklists for progress tracking
- [ ] Feedback mechanism
- [ ] Mentor assignments
- [ ] Expected timeline (day/week/month)
```


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

