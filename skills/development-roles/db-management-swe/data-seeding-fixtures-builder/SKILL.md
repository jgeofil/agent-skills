---
name: data-seeding-fixtures-builder
description: >-
  Generates deterministic seed data for development and testing with factory functions, realistic fixtures, and database reset scripts. Use for "data seeding", "test fixtures", "database seeding", or "mock data generation".
license: MIT
metadata:
  version: "1.0"
  category: db-management-swe
---

# Data Seeding & Fixtures Builder

Generate realistic, deterministic seed data for development and testing.

## Seed Data Strategy

```typescript
// prisma/seed.ts
import { PrismaClient } from "@prisma/client";
import { faker } from "@faker-js/faker";

const prisma = new PrismaClient();

async function main() {
  console.log("🌱 Seeding database...");

  // Clear existing data
  await prisma.order.deleteMany();
  await prisma.user.deleteMany();

  // Seed users
  const users = await seedUsers(10);
  console.log(`✅ Created ${users.length} users`);

  // Seed orders
  const orders = await seedOrders(users, 50);
  console.log(`✅ Created ${orders.length} orders`);

  console.log("✅ Seeding complete!");
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
```

## Factory Functions

```typescript
// factories/user.factory.ts
import { faker } from "@faker-js/faker";
import { PrismaClient, User } from "@prisma/client";

const prisma = new PrismaClient();

export interface UserFactoryOptions {
  email?: string;
  name?: string;
  role?: "USER" | "ADMIN";
}

export class UserFactory {
  static async create(options: UserFactoryOptions = {}): Promise<User> {
    return prisma.user.create({
      data: {
        email: options.email || faker.internet.email(),
        name: options.name || faker.person.fullName(),
        role: options.role || "USER",
        createdAt: faker.date.past(),
      },
    });
  }

  static async createMany(
    count: number,
    options: UserFactoryOptions = {}
  ): Promise<User[]> {
    return Promise.all(
      Array.from({ length: count }, () => this.create(options))
    );
  }

  static async createAdmin(): Promise<User> {
    return this.create({ role: "ADMIN" });
  }
}

// Usage:
// const user = await UserFactory.create();
// const admin = await UserFactory.createAdmin();
// const users = await UserFactory.createMany(10);
```

## Best Practices

1. **Use factories**: Reusable data generation
2. **Deterministic in tests**: Fixed seed values
3. **Realistic fixtures**: Production-like data
4. **Environment-specific**: Different needs per environment
5. **Cleanup after tests**: Avoid pollution
6. **Relationship integrity**: Proper foreign keys
7. **Performance**: Batch inserts for large datasets

## Output Checklist

- [ ] Seed script created
- [ ] Factory functions for each model
- [ ] Realistic fixtures defined
- [ ] Deterministic seeding (tests)
- [ ] Relationship building logic
- [ ] Environment-specific seeds
- [ ] Database reset script
- [ ] E2E test fixtures


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

