---
name: mermaid-diagram-generator
description: >-
  Creates Mermaid diagrams for flowcharts, sequence diagrams, ERDs, and architecture visualizations in markdown. Use when users request "Mermaid diagram", "flowchart", "sequence diagram", "ERD diagram", or "architecture diagram".
license: MIT
metadata:
  version: "1.0"
  category: maintenance-swe
---

# Mermaid Diagram Generator

Create clear, maintainable diagrams using Mermaid syntax in markdown.

## Core Workflow

1. **Identify diagram type**: Flow, sequence, ERD, etc.
2. **Define elements**: Nodes, connections, labels
3. **Apply styling**: Colors, shapes, directions
4. **Add interactions**: Click handlers (optional)
5. **Embed in docs**: Markdown integration

## Flowchart Diagrams

### Basic Flowchart

```mermaid
flowchart TD
    A[Start] --> B{Is user logged in?}
    B -->|Yes| C[Show Dashboard]
    B -->|No| D[Show Login Page]
    D --> E[Enter Credentials]
    E --> F{Valid credentials?}
    F -->|Yes| C
    F -->|No| G[Show Error]
    G --> D
    C --> H[End]
```

### Node Shapes

```mermaid
flowchart LR
    A[Rectangle] --> B(Rounded)
    B --> C([Stadium])
    C --> D[[Subroutine]]
    D --> E[(Database)]
    E --> F((Circle))
    F --> G>Asymmetric]
    G --> H{Diamond}
    H --> I{{Hexagon}}
    I --> J[/Parallelogram/]
    J --> K[\Parallelogram Alt\]
    K --> L[/Trapezoid\]
    L --> M[\Trapezoid Alt/]
```

### Subgraphs

```mermaid
flowchart TB
    subgraph Frontend
        A[React App] --> B[Redux Store]
        B --> C[Components]
    end

    subgraph Backend
        D[API Gateway] --> E[Auth Service]
        D --> F[User Service]
        D --> G[Order Service]
    end

    subgraph Database
        H[(PostgreSQL)]
        I[(Redis Cache)]
    end

    C --> D
    E --> H
    F --> H
    G --> H
    E --> I
```

### Styled Flowchart

```mermaid
flowchart TD
    A[Request] --> B{Rate Limited?}
    B -->|Yes| C[429 Too Many Requests]
    B -->|No| D{Authenticated?}
    D -->|No| E[401 Unauthorized]
    D -->|Yes| F{Authorized?}
    F -->|No| G[403 Forbidden]
    F -->|Yes| H[Process Request]
    H --> I[200 OK]

    style A fill:#e1f5fe
    style I fill:#c8e6c9
    style C fill:#ffcdd2
    style E fill:#ffcdd2
    style G fill:#ffcdd2

    classDef error fill:#ffcdd2,stroke:#c62828
    classDef success fill:#c8e6c9,stroke:#2e7d32
    class C,E,G error
    class I success
```

## Best Practices

1. **Keep it simple**: Avoid overcrowded diagrams
2. **Use subgraphs**: Group related elements
3. **Consistent styling**: Define class styles
4. **Direction matters**: LR for processes, TD for hierarchies
5. **Add notes**: Clarify complex parts
6. **Use icons**: Font Awesome integration
7. **Version control**: Diagrams are code
8. **Document purpose**: Add titles and descriptions

## Output Checklist

Every Mermaid diagram should include:

- [ ] Appropriate diagram type
- [ ] Clear node labels
- [ ] Logical flow direction
- [ ] Subgraphs for grouping
- [ ] Consistent styling
- [ ] Meaningful connections
- [ ] Notes where needed
- [ ] Title or description
- [ ] Proper syntax validation
- [ ] Readable at expected size


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

