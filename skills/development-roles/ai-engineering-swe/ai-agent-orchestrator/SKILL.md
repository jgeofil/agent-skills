---
name: ai-agent-orchestrator
description: >-
  Orchestrates multi-agent AI systems with task delegation, agent communication, shared memory, and workflow coordination. Use when users request "multi-agent system", "agent orchestration", "AI agents", "agent coordination", or "autonomous agents".
license: MIT
metadata:
  version: "1.0"
  category: ai-engineering-swe
---

# AI Agent Orchestrator

Build coordinated multi-agent systems for complex task automation.

## Core Workflow

1. **Define agents**: Create specialized agents
2. **Design workflow**: Plan agent coordination
3. **Implement handoffs**: Agent-to-agent communication
4. **Add shared memory**: Persistent context
5. **Create supervisor**: Orchestrate execution
6. **Monitor execution**: Track agent activities

## Agent Architecture

### Agent Definition

```typescript
// agents/base.ts
import { ChatOpenAI } from '@langchain/openai';
import { SystemMessage, HumanMessage, AIMessage } from '@langchain/core/messages';

export interface AgentConfig {
  name: string;
  role: string;
  systemPrompt: string;
  tools?: Tool[];
  model?: string;
}

export interface AgentResponse {
  content: string;
  toolCalls?: ToolCall[];
  nextAgent?: string;
  completed?: boolean;
}

export class Agent {
  private model: ChatOpenAI;
  private config: AgentConfig;
  private messageHistory: BaseMessage[] = [];

  constructor(config: AgentConfig) {
    this.config = config;
    this.model = new ChatOpenAI({
      modelName: config.model || 'gpt-4-turbo-preview',
      temperature: 0.7,
    });
  }

  async execute(input: string, context?: Record<string, any>): Promise<AgentResponse> {
    const systemMessage = new SystemMessage(
      this.buildSystemPrompt(context)
    );

    const messages = [
      systemMessage,
      ...this.messageHistory,
      new HumanMessage(input),
    ];

    const response = await this.model.invoke(messages, {
      tools: this.config.tools,
    });

    this.messageHistory.push(new HumanMessage(input));
    this.messageHistory.push(new AIMessage(response.content as string));

    return this.parseResponse(response);
  }

  private buildSystemPrompt(context?: Record<string, any>): string {
    let prompt = this.config.systemPrompt;

    if (context) {
      prompt += `\n\nContext:\n${JSON.stringify(context, null, 2)}`;
    }

    return prompt;
  }

  private parseResponse(response: any): AgentResponse {
    // Parse tool calls and determine next actions
    return {
      content: response.content as string,
      toolCalls: response.tool_calls,
      completed: response.content?.includes('[TASK_COMPLETE]'),
    };
  }

  clearHistory() {
    this.messageHistory = [];
  }
}
```

### Specialized Agents

```typescript
// agents/specialists.ts
import { Agent, AgentConfig } from './base';

export const ResearchAgent = new Agent({
  name: 'researcher',
  role: 'Research Specialist',
  systemPrompt: `You are a research specialist. Your job is to:
- Search for and gather relevant information
- Analyze sources and extract key insights
- Summarize findings clearly
- Cite sources when possible

When you have gathered sufficient information, include [TASK_COMPLETE] in your response.
If you need help from another agent, specify: [HANDOFF:agent_name]`,
  tools: [searchTool, webScrapeTool],
});

export const WriterAgent = new Agent({
  name: 'writer',
  role: 'Content Writer',
  systemPrompt: `You are a professional content writer. Your job is to:
- Create engaging, well-structured content
- Adapt tone and style to the target audience
- Incorporate research and data effectively
- Edit and refine for clarity

Use the research provided to create compelling content.
When complete, include [TASK_COMPLETE].`,
});

export const ReviewerAgent = new Agent({
  name: 'reviewer',
  role: 'Quality Reviewer',
  systemPrompt: `You are a quality reviewer. Your job is to:
- Review content for accuracy and clarity
- Check for errors and inconsistencies
- Suggest improvements
- Approve or request revisions

Provide specific feedback. If approved, include [APPROVED].
If revisions needed, include [REVISIONS_NEEDED] with specific changes.`,
});

export const PlannerAgent = new Agent({
  name: 'planner',
  role: 'Task Planner',
  systemPrompt: `You are a task planner. Your job is to:
- Break down complex tasks into subtasks
- Identify which specialist agent should handle each subtask
- Create an execution order
- Track progress

Output a structured plan in JSON format:
{
  "goal": "...",
  "steps": [
    { "step": 1, "agent": "researcher", "task": "..." },
    { "step": 2, "agent": "writer", "task": "..." }
  ]
}`,
});
```

## Best Practices

1. **Single responsibility**: Each agent has one clear role
2. **Clear handoffs**: Explicit agent-to-agent communication
3. **Shared context**: Use memory for persistent state
4. **Iteration limits**: Prevent infinite loops
5. **Error handling**: Graceful degradation
6. **Observability**: Log all agent actions
7. **Testing**: Test agents individually and together
8. **Timeout handling**: Prevent stuck agents

## Output Checklist

Every agent system should include:

- [ ] Agent base class with common functionality
- [ ] Specialized agents with clear roles
- [ ] Orchestrator for coordination
- [ ] Shared memory system
- [ ] Event-based communication
- [ ] Workflow definitions
- [ ] Error handling and retries
- [ ] Iteration limits
- [ ] Logging and monitoring
- [ ] Agent handoff protocol


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)
- [Single Agent Loop Planning](references/single-agent-loop-planning.md)

