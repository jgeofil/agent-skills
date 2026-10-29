---
name: crewai-agent-architect
description: Design optimized CrewAI agent specifications, backstories, and configurations. Use when the user asks to create or prompt a CrewAI agent, design agent roles, goals, or backstories, configure delegation and tools, or structure multi-agent team roles in CrewAI.
---

# CrewAI Agent Architect

A specialized skill for authoring robust, production-grade CrewAI agent definitions adhering to official CrewAI best practices, clean configuration schemas, and collaborative multi-agent patterns.

## When to Use

- Defining a CrewAI agent within a multi-agent team.
- Generating CrewAI agent personas, roles, goals, and backstories.
- Configuring CrewAI delegation, planning capabilities, standard tools, and LLM backings.
- Translating functional domain requirements into YAML and Python agent configurations.

## Core Requirements

Every generated agent specification must deliver five primary pillars:

1. **Role**: The agent functional specialty and title within the team hierarchy.
2. **Goal**: The agent clear objective, key deliverables, and measurable outcomes.
3. **Backstory**: Rich persona narrative driving tone, decision heuristics, domain authority, and execution focus.
4. **PlanningEnabled**: Boolean flag and architectural rationale indicating whether step-by-step reasoning or internal planning is activated.
5. **CanDelegate**: Boolean flag indicating delegation permission (`allow_delegation`), including brief profiles of target collaborator agents if enabled.

Additionally, provide recommended CrewAI built-in tools (`crewai_tools`) and optimal LLM model tiers based on reasoning depth and operational latency.

## Best Practices for CrewAI Agents

- **Avoid Generic Personas**: Ground the backstory in operational methodology, edge-case vigilance, and communication standards rather than decorative adjectives.
- **Clarify Team Boundaries**: Explicitly state what the agent handles and what it hands off or leaves to teammates.
- **Selective Delegation**: Set `allow_delegation=True` primarily for orchestrators, managers, or coordinators. Specialist executors should keep `allow_delegation=False` to prevent circular handoffs and token waste.
- **Tool Discipline**: Assign only necessary tools from `crewai_tools` (such as `SerperDevTool`, `FileReadTool`, or `CodeInterpreterTool`). Excess tools degrade routing accuracy.
- **Model Pairing**: Pair complex reasoning tasks (planning, code generation, auditing) with frontier models, and bounded extraction/formatting tasks with faster, cost-efficient models.

## Workflow

1. **Analyze Requirements**: Determine the agent domain, responsibilities, and position in the crew hierarchy.
2. **Define Agent Pillars**:
   - Formulate a concise, active-voice `Role`.
   - Specify a concrete `Goal` with deliverables.
   - Draft an authoritative `Backstory` incorporating operational heuristics and quality bars.
   - Evaluate whether `PlanningEnabled` (`planning=True` on the Crew or agent callback) is required.
   - Evaluate whether `CanDelegate` (`allow_delegation=True/False`) is safe and beneficial.
3. **Select Tools and LLM**: Recommend appropriate tools from the `crewai_tools` suite and state LLM reasoning tiers.
4. **Output Formats**: Present the definition in both standard `config/agents.yaml` format and Python `Agent(...)` instantiation syntax.

## Gotchas

- Setting delegation to true on multiple peer agents can create circular question loops.
- Backstories that lack concrete operating constraints produce verbose, ungrounded agent responses.
- Ensure tool names match official `crewai_tools` modules.
