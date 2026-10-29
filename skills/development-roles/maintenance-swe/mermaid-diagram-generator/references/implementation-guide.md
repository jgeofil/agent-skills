# Mermaid Diagram Generator - Implementation Guide & Code Recipes

## Sequence Diagrams

### API Request Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Client
    participant API
    participant Auth
    participant DB

    User->>Client: Click Login
    Client->>API: POST /auth/login
    API->>Auth: Validate credentials
    Auth->>DB: Query user
    DB-->>Auth: User data
    Auth-->>API: JWT token
    API-->>Client: 200 OK + token
    Client->>Client: Store token
    Client-->>User: Show dashboard
```

### With Loops and Conditions

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    participant Q as Queue
    participant W as Worker

    C->>S: Submit job
    S->>Q: Enqueue job
    S-->>C: Job ID

    loop Poll status
        C->>S: GET /jobs/{id}
        S-->>C: Status: processing
    end

    W->>Q: Dequeue job
    W->>W: Process job

    alt Success
        W->>S: Job completed
        S-->>C: Status: completed
    else Failure
        W->>S: Job failed
        S-->>C: Status: failed
    end
```

### With Notes and Activations

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant D as Database

    Note over U,D: User Registration Flow

    U->>+F: Fill registration form
    F->>F: Validate input
    F->>+B: POST /api/users

    activate B
    B->>B: Hash password
    B->>+D: INSERT user
    D-->>-B: User created
    B->>B: Generate verification email
    deactivate B

    B-->>-F: 201 Created
    F-->>-U: Success message

    Note right of B: Email sent async
```

## Entity Relationship Diagrams

### Database Schema

```mermaid
erDiagram
    USERS ||--o{ ORDERS : places
    USERS ||--o{ REVIEWS : writes
    USERS {
        uuid id PK
        string email UK
        string password_hash
        string name
        timestamp created_at
        timestamp updated_at
    }

    ORDERS ||--|{ ORDER_ITEMS : contains
    ORDERS {
        uuid id PK
        uuid user_id FK
        decimal total
        string status
        timestamp created_at
    }

    PRODUCTS ||--o{ ORDER_ITEMS : "ordered in"
    PRODUCTS ||--o{ REVIEWS : "reviewed in"
    PRODUCTS {
        uuid id PK
        string name
        text description
        decimal price
        int stock
        uuid category_id FK
    }

    ORDER_ITEMS {
        uuid id PK
        uuid order_id FK
        uuid product_id FK
        int quantity
        decimal price
    }

    CATEGORIES ||--o{ PRODUCTS : contains
    CATEGORIES {
        uuid id PK
        string name
        uuid parent_id FK
    }

    REVIEWS {
        uuid id PK
        uuid user_id FK
        uuid product_id FK
        int rating
        text content
        timestamp created_at
    }
```

## State Diagrams

### Order State Machine

```mermaid
stateDiagram-v2
    [*] --> Pending: Order created

    Pending --> Processing: Payment received
    Pending --> Cancelled: User cancels

    Processing --> Shipped: Items dispatched
    Processing --> Cancelled: Out of stock

    Shipped --> Delivered: Package delivered
    Shipped --> Returned: Return requested

    Delivered --> Returned: Return requested
    Delivered --> [*]: Complete

    Returned --> Refunded: Refund processed
    Refunded --> [*]

    Cancelled --> [*]

    note right of Processing
        Inventory checked
        and reserved
    end note
```

### With Composite States

```mermaid
stateDiagram-v2
    [*] --> Idle

    state Active {
        [*] --> Running
        Running --> Paused: pause
        Paused --> Running: resume
        Running --> [*]: complete
    }

    Idle --> Active: start
    Active --> Idle: stop
    Active --> Error: error
    Error --> Idle: reset
```

## Class Diagrams

### TypeScript Classes

```mermaid
classDiagram
    class User {
        +string id
        +string email
        +string name
        -string passwordHash
        +login(password: string) boolean
        +updateProfile(data: ProfileData) void
        +getOrders() Order[]
    }

    class Order {
        +string id
        +string userId
        +OrderItem[] items
        +OrderStatus status
        +decimal total
        +addItem(product: Product, qty: number) void
        +removeItem(itemId: string) void
        +checkout() boolean
    }

    class OrderItem {
        +string id
        +string productId
        +number quantity
        +decimal price
    }

    class Product {
        +string id
        +string name
        +decimal price
        +number stock
        +reserve(qty: number) boolean
        +release(qty: number) void
    }

    User "1" --> "*" Order: places
    Order "1" --> "*" OrderItem: contains
    OrderItem "*" --> "1" Product: references

    class OrderStatus {
        <<enumeration>>
        PENDING
        PROCESSING
        SHIPPED
        DELIVERED
        CANCELLED
    }
```

## Architecture Diagrams

### C4 Context Diagram

```mermaid
flowchart TB
    subgraph boundary[System Boundary]
        system[E-commerce Platform]
    end

    user[fa:fa-user Customer]
    admin[fa:fa-user-cog Admin]

    payment[fa:fa-credit-card Payment Provider]
    shipping[fa:fa-truck Shipping API]
    email[fa:fa-envelope Email Service]

    user --> system
    admin --> system
    system --> payment
    system --> shipping
    system --> email

    style system fill:#438dd5,color:#fff
    style user fill:#08427b,color:#fff
    style admin fill:#08427b,color:#fff
    style payment fill:#999,color:#fff
    style shipping fill:#999,color:#fff
    style email fill:#999,color:#fff
```

### Microservices Architecture

```mermaid
flowchart TB
    subgraph Client Layer
        web[Web App]
        mobile[Mobile App]
    end

    subgraph API Layer
        gateway[API Gateway]
        auth[Auth Service]
    end

    subgraph Services
        users[User Service]
        orders[Order Service]
        products[Product Service]
        payments[Payment Service]
        notifications[Notification Service]
    end

    subgraph Data Layer
        pg1[(Users DB)]
        pg2[(Orders DB)]
        pg3[(Products DB)]
        redis[(Redis Cache)]
        kafka[Kafka]
    end

    web --> gateway
    mobile --> gateway
    gateway --> auth
    gateway --> users
    gateway --> orders
    gateway --> products

    users --> pg1
    orders --> pg2
    products --> pg3

    users --> redis
    products --> redis

    orders --> kafka
    payments --> kafka
    notifications --> kafka

    kafka --> payments
    kafka --> notifications
```

## Git Graph

```mermaid
gitGraph
    commit id: "Initial commit"
    branch develop
    checkout develop
    commit id: "Setup project"
    commit id: "Add components"
    branch feature/auth
    checkout feature/auth
    commit id: "Add login"
    commit id: "Add signup"
    checkout develop
    merge feature/auth id: "Merge auth"
    branch feature/dashboard
    checkout feature/dashboard
    commit id: "Add dashboard"
    checkout develop
    merge feature/dashboard id: "Merge dashboard"
    checkout main
    merge develop id: "Release v1.0" tag: "v1.0.0"
```

## Pie Charts

```mermaid
pie showData
    title Technology Stack Distribution
    "TypeScript" : 45
    "React" : 25
    "Node.js" : 15
    "PostgreSQL" : 10
    "Other" : 5
```

## Timeline

```mermaid
timeline
    title Project Roadmap 2024
    section Q1
        January : Project Kickoff
                : Team Setup
        February : MVP Development
        March : Alpha Release
    section Q2
        April : Beta Testing
        May : Bug Fixes
        June : Public Launch
    section Q3
        July : Feature Expansion
        August : Performance Optimization
        September : Mobile App
    section Q4
        October : Enterprise Features
        November : International Expansion
        December : Year Review
```

## Mindmap

```mermaid
mindmap
    root((Project))
        Frontend
            React
            Next.js
            Tailwind CSS
        Backend
            Node.js
            Express
            GraphQL
        Database
            PostgreSQL
            Redis
            MongoDB
        DevOps
            Docker
            Kubernetes
            CI/CD
        Testing
            Jest
            Cypress
            Playwright
```
