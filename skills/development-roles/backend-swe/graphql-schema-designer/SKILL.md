---
name: graphql-schema-designer
description: >-
  Designs GraphQL schemas with types, queries, mutations, subscriptions, resolvers, and DataLoader patterns for efficient data fetching. Use when users request "GraphQL API", "schema design", "GraphQL setup", "resolvers", or "Apollo Server".
license: MIT
metadata:
  version: "1.0"
  category: backend-swe
---

# GraphQL Schema Designer

Build efficient, type-safe GraphQL APIs with proper schema design and resolver patterns.

## Core Workflow

1. **Design schema**: Define types, queries, mutations
2. **Implement resolvers**: Connect to data sources
3. **Add DataLoader**: Batch and cache queries
4. **Enable subscriptions**: Real-time updates
5. **Add validation**: Input validation and errors
6. **Document**: Schema descriptions

## Project Setup

```bash
npm install @apollo/server graphql graphql-tag dataloader
npm install -D @graphql-codegen/cli @graphql-codegen/typescript
```

## Schema Design

### Type Definitions

```graphql
# schema.graphql
scalar DateTime
scalar JSON

"""
A registered user in the system
"""
type User {
  id: ID!
  email: String!
  name: String!
  avatar: String
  role: UserRole!
  posts: [Post!]!
  comments: [Comment!]!
  createdAt: DateTime!
  updatedAt: DateTime!
}

enum UserRole {
  ADMIN
  USER
  GUEST
}

type Post {
  id: ID!
  title: String!
  content: String!
  published: Boolean!
  author: User!
  comments: [Comment!]!
  tags: [Tag!]!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Comment {
  id: ID!
  content: String!
  author: User!
  post: Post!
  createdAt: DateTime!
}

type Tag {
  id: ID!
  name: String!
  posts: [Post!]!
}

"""
Pagination info for cursor-based pagination
"""
type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

type PostEdge {
  cursor: String!
  node: Post!
}

type PostConnection {
  edges: [PostEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}
```

### Queries

```graphql
type Query {
  """
  Get current authenticated user
  """
  me: User

  """
  Get a user by ID
  """
  user(id: ID!): User

  """
  List all users with optional filtering
  """
  users(
    role: UserRole
    search: String
    limit: Int = 10
    offset: Int = 0
  ): [User!]!

  """
  Get a post by ID
  """
  post(id: ID!): Post

  """
  List posts with cursor pagination
  """
  posts(
    first: Int
    after: String
    last: Int
    before: String
    published: Boolean
    authorId: ID
  ): PostConnection!

  """
  Search posts by title or content
  """
  searchPosts(query: String!, limit: Int = 10): [Post!]!
}
```

### Mutations

```graphql
input CreateUserInput {
  email: String!
  name: String!
  password: String!
  role: UserRole = USER
}

input UpdateUserInput {
  name: String
  avatar: String
}

input CreatePostInput {
  title: String!
  content: String!
  published: Boolean = false
  tagIds: [ID!]
}

input UpdatePostInput {
  title: String
  content: String
  published: Boolean
  tagIds: [ID!]
}

type Mutation {
  # Auth
  signUp(input: CreateUserInput!): AuthPayload!
  signIn(email: String!, password: String!): AuthPayload!
  signOut: Boolean!

  # Users
  updateUser(id: ID!, input: UpdateUserInput!): User!
  deleteUser(id: ID!): Boolean!

  # Posts
  createPost(input: CreatePostInput!): Post!
  updatePost(id: ID!, input: UpdatePostInput!): Post!
  deletePost(id: ID!): Boolean!
  publishPost(id: ID!): Post!

  # Comments
  createComment(postId: ID!, content: String!): Comment!
  deleteComment(id: ID!): Boolean!
}

type AuthPayload {
  token: String!
  user: User!
}
```

### Subscriptions

```graphql
type Subscription {
  """
  Subscribe to new posts
  """
  postCreated: Post!

  """
  Subscribe to comments on a specific post
  """
  commentAdded(postId: ID!): Comment!

  """
  Subscribe to post updates
  """
  postUpdated(id: ID!): Post!
}
```

## Best Practices

1. **Use DataLoader**: Prevent N+1 queries
2. **Design schema first**: API-first approach
3. **Use cursor pagination**: For large datasets
4. **Add descriptions**: Document every type and field
5. **Handle errors properly**: Custom error types
6. **Generate types**: Use codegen for type safety
7. **Validate inputs**: Sanitize before processing
8. **Use subscriptions sparingly**: Only for real-time needs

## Output Checklist

Every GraphQL API should include:

- [ ] Well-designed type definitions
- [ ] Queries with proper filtering/pagination
- [ ] Mutations with input validation
- [ ] DataLoader for batching
- [ ] Custom error types
- [ ] Authentication/authorization
- [ ] Code generation setup
- [ ] Schema documentation
- [ ] Subscription support (if needed)
- [ ] Rate limiting


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

