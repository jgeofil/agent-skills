---
name: explaining-code
description: >-
  Explains complex code, algorithms, and system architectures using intuitive analogies, ASCII/Mermaid flow diagrams, step-by-step execution traces, and common pitfall warnings. Use when teaching about a codebase, onboarding engineers, conducting code reviews, or when the user asks "how does this work?" or "explain this code".
license: MIT
metadata:
  version: "1.0"
  category: maintenance-swe
---

# Explaining Code

Deliver clear, memorable technical explanations that bridge abstract code logic with intuitive mental models and structural diagrams.

## When to Use This Skill

- Onboarding engineers to unfamiliar repositories or legacy subsystems
- Explaining complex algorithms, concurrency flows, or distributed state
- Answering user prompts like "how does this work?", "walk me through this code", or "explain this function"
- Documenting architectural invariants and non-obvious design decisions

## The 4-Part Pedagogical Framework

Every code explanation should follow this progression:

1. **The Core Analogy**: Anchor the unfamiliar concept to an intuitive everyday mental model.
2. **Visual Flow Diagram**: Provide an ASCII or Mermaid diagram depicting component interaction and data flow.
3. **Step-by-Step Code Trace**: Walk through the critical execution path with annotated code snippets.
4. **Gotchas & Edge Cases**: Highlight common misconceptions, failure modes, and performance traps.

## Execution Walkthrough Template

```text
Input Request -> [ Layer 1: Analogy ] -> Sets intuitive context
              -> [ Layer 2: Diagram ] -> Maps structural boundaries
              -> [ Layer 3: Trace   ] -> Walks runtime execution
              -> [ Layer 4: Gotcha  ] -> Highlights traps & invariants
```

### 1. Analogy Example
- *Concept*: Connection Pooling.
- *Analogy*: "A taxi dispatch stand at an airport. Instead of buying a new car every time a passenger arrives and crushing it when the trip finishes, a pool of cars is kept idling and reused."

### 2. Diagram Example
```text
Client Request
      |
      v
[ Connection Pool ] ---> Idle connection available?
      |                         |
     YES                       NO
      |                         |
      v                         v
Acquire & Query           Wait or Spawn (up to max_size)
      |                         |
      +---------> Release <-----+
```

### 3. Step-by-Step Walkthrough Rules
- Trace variable states across iterations or async hops.
- Explain *why* a particular data structure or pattern was chosen.
- Keep prose concise and conversational; avoid robotic paraphrasing of syntax.

### 4. Gotcha Highlights
- Call out concurrency hazards (race conditions, deadlocks).
- Note scale limits (O(N^2) loops, missing database indexes).
