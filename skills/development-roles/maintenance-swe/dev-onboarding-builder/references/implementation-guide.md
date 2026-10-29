# Developer Onboarding Builder - Implementation Guide & Code Recipes

## Day 1: Your First Task

### Task: Fix a Starter Issue

We've labeled some issues as `good-first-issue` for new team members.

**Goal:** Successfully complete one small PR to learn our workflow

**Steps:**

1. Browse [good first issues](https://github.com/company/project/labels/good-first-issue)
2. Pick one that interests you (or ask for suggestion in #dev-onboarding)
3. Comment on the issue: "I'll take this!"
4. Create a branch: `git checkout -b fix/issue-123-description`
5. Make your changes
6. Write/update tests
7. Run `pnpm lint` and `pnpm test`
8. Commit following [conventions](./CONTRIBUTING.md#commit-messages)
9. Push and create PR
10. Request review from your mentor

**Estimated time:** 2-4 hours

**Success criteria:**

- [ ] Branch created with proper name
- [ ] Code changes made
- [ ] Tests written/updated
- [ ] All checks passing
- [ ] PR created with description
- [ ] Code reviewed and merged

**Mentors:** @alice (backend), @bob (frontend), @charlie (full-stack)

## Day 2-3: Codebase Tour

### Project Structure Overview

```
src/
├── app/              # Next.js routes (start here!)
│   ├── api/          # API endpoints
│   └── (auth)/       # Authentication pages
├── components/       # React components
│   ├── ui/           # Base UI components
│   └── features/     # Feature-specific components
├── lib/              # Utilities and helpers
│   ├── api/          # API client
│   ├── hooks/        # Custom React hooks
│   └── utils/        # Helper functions
├── services/         # Business logic layer
└── types/            # TypeScript definitions
```

### Key Files to Understand

| File                 | What It Does            | When You'll Touch It    |
| -------------------- | ----------------------- | ----------------------- |
| `src/app/layout.tsx` | Root layout & providers | Adding global providers |
| `src/lib/db.ts`      | Database client         | Database queries        |
| `src/lib/auth.ts`    | Authentication logic    | Auth-related features   |
| `src/middleware.ts`  | Request middleware      | Adding auth/redirects   |

### Walking Tour (Read These Files in Order)

1. **`src/app/page.tsx`** - Homepage (entry point)
2. **`src/app/api/users/route.ts`** - Simple API endpoint
3. **`src/services/user.service.ts`** - Business logic example
4. **`src/components/ui/button.tsx`** - UI component pattern
5. **`src/lib/hooks/useUser.ts`** - Custom hook example

**Exercise:** Find the code that handles user registration. Hint: Start at the API route!

### Common Patterns

**API Route Pattern**

```typescript
// src/app/api/[resource]/route.ts
export async function GET(req: Request) {
  // 1. Validate auth
  // 2. Parse request
  // 3. Call service layer
  // 4. Return response
}
```

**Service Layer Pattern**

```typescript
// src/services/[resource].service.ts
export class UserService {
  async create(data: CreateUserDto) {
    // 1. Validate data
    // 2. Business logic
    // 3. Database operation
    // 4. Return result
  }
}
```

## Week 1: Learning Path

### Day 1

- [ ] Complete environment setup
- [ ] Fix first issue
- [ ] Meet your team (schedule 1:1s)

### Day 2-3

- [ ] Read codebase tour documents
- [ ] Complete second issue (medium complexity)
- [ ] Review 2-3 PRs from teammates

### Day 4-5

- [ ] Work on first feature (with mentor pairing)
- [ ] Attend team standup/planning
- [ ] Set up development tools (linters, extensions)

## Team Structure

### Engineering Team

**Alice (@alice)** - Tech Lead

- Approves architecture decisions
- Code review on complex PRs
- Ask: System design questions

**Bob (@bob)** - Senior Backend Engineer

- Database and API expert
- Ask: Backend, performance questions

**Charlie (@charlie)** - Senior Frontend Engineer

- UI/UX implementation
- Ask: React, styling questions

**Your Manager (@manager)**

- Weekly 1:1s on Fridays 2pm
- Career development discussions
- Ask: Process, priorities, career questions

### Communication Channels

- **#dev-general** - General development discussion
- **#dev-help** - Ask questions, get unstuck
- **#dev-onboarding** - New member support
- **#dev-releases** - Release announcements
- **#dev-alerts** - Production alerts

### Meeting Schedule

- **Daily Standup** - 10:00 AM (15 min)
- **Sprint Planning** - Mondays 2:00 PM (1 hour)
- **Team Retro** - Fridays 4:00 PM (45 min)
- **Tech Talks** - Thursdays 3:00 PM (30 min)

## Development Workflow

### Daily Workflow

1. **Morning:** Check Slack, pull latest main
2. **Standup:** Share yesterday, today, blockers
3. **Code:** Work on assigned tickets
4. **Lunch:** Team usually eats at 12:30
5. **Afternoon:** Continue coding, review PRs
6. **End of day:** Update ticket status, push work

### PR Review Guidelines

When reviewing PRs:

- [ ] Check code quality and style
- [ ] Verify tests cover changes
- [ ] Run the code locally if significant
- [ ] Ask questions if unclear
- [ ] Approve when satisfied

### Getting Code Reviewed

When requesting review:

- [ ] Self-review first
- [ ] Add clear description
- [ ] Link related issues
- [ ] Tag appropriate reviewers
- [ ] Address feedback promptly

## Common Gotchas

### Database

**Problem:** `relation "users" does not exist`
**Solution:** Run migrations: `pnpm db:migrate`

**Problem:** Seed data not appearing
**Solution:** Reset database: `pnpm db:reset`

### Development Server

**Problem:** Changes not reflecting
**Solution:**

1. Hard refresh (Cmd+Shift+R)
2. Clear .next folder: `rm -rf .next`
3. Restart dev server

**Problem:** Port already in use
**Solution:** Kill process: `lsof -ti:3000 | xargs kill`

### Environment

**Problem:** Missing environment variable
**Solution:** Check .env.example, add to your .env

**Problem:** API key not working
**Solution:** Verify it's the dev key, not prod (ask team)

## Resources

### Documentation

- [Architecture Overview](./ARCHITECTURE.md)
- [API Reference](./docs/API.md)
- [Contributing Guide](./CONTRIBUTING.md)
- [Style Guide](./docs/STYLE_GUIDE.md)

### Learning Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Prisma Guides](https://www.prisma.io/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

### Internal Resources

- Company Wiki: https://wiki.company.com
- Design System: https://design.company.com
- API Playground: https://api-dev.company.com

## Getting Help

### When You're Stuck (5-15-30 Rule)

- **5 minutes:** Try to solve it yourself
- **15 minutes:** Search docs, Stack Overflow, past issues
- **30 minutes:** Ask in #dev-help with context

### Good Question Template

```
**What I'm trying to do:** [goal]
**What I tried:** [attempts]
**Error message:** [full error]
**Environment:** [OS, Node version, etc.]
**Related code:** [link to file/line]
```

### Who to Ask

- **Setup issues:** #dev-onboarding or #dev-help
- **Code questions:** #dev-help or your mentor
- **Process questions:** Your manager
- **Urgent/production:** #dev-alerts
