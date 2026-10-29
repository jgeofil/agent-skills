---
name: mcp-server-builder
description: >-
  Builds Model Context Protocol (MCP) servers for Claude with tools, resources, and prompts. Use when users request "create MCP server", "build Claude tool", "MCP integration", or "custom Claude tools".
license: MIT
metadata:
  version: "1.0"
  category: ai-engineering-swe
---

# MCP Server Builder

Create Model Context Protocol servers to extend Claude's capabilities with custom tools and resources.

## Core Workflow

1. **Define purpose**: Identify what capabilities to add
2. **Choose transport**: stdio (local) or HTTP/SSE (remote)
3. **Design tools**: Define tool schemas and handlers
4. **Add resources**: Optional file/data access
5. **Create prompts**: Optional reusable prompts
6. **Test locally**: Verify with MCP inspector
7. **Deploy**: Configure for Claude Desktop or API

## MCP Architecture Overview

```
┌─────────────┐     MCP Protocol      ┌─────────────┐
│   Claude    │◄────────────────────►│ MCP Server  │
│   (Host)    │  JSON-RPC over stdio  │  (Your App) │
└─────────────┘                       └─────────────┘
                                            │
                                            ▼
                                      ┌───────────┐
                                      │  Tools    │
                                      │ Resources │
                                      │  Prompts  │
                                      └───────────┘
```

## Project Setup

### TypeScript MCP Server

```bash
# Create project
mkdir my-mcp-server && cd my-mcp-server
npm init -y

# Install dependencies
npm install @modelcontextprotocol/sdk zod

# Dev dependencies
npm install -D typescript @types/node tsx
```

```json
// package.json
{
  "name": "my-mcp-server",
  "version": "1.0.0",
  "type": "module",
  "main": "dist/index.js",
  "bin": {
    "my-mcp-server": "./dist/index.js"
  },
  "scripts": {
    "build": "tsc",
    "dev": "tsx watch src/index.ts",
    "start": "node dist/index.js"
  }
}
```

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "declaration": true
  },
  "include": ["src/**/*"]
}
```

## Best Practices

1. **Validate inputs**: Use Zod or similar for schema validation
2. **Handle errors gracefully**: Return meaningful error messages
3. **Use environment variables**: Never hardcode secrets
4. **Rate limit external calls**: Respect API limits
5. **Log appropriately**: Use stderr for logs (stdout is for MCP)
6. **Document tools well**: Clear descriptions help Claude use them correctly
7. **Keep tools focused**: Single responsibility per tool
8. **Test with inspector**: Verify behavior before deployment

## Output Checklist

Every MCP server should include:

- [ ] Server with name and version
- [ ] Capabilities declaration (tools/resources/prompts)
- [ ] Tool schemas with descriptions
- [ ] Input validation with clear error messages
- [ ] Proper error handling and MCP error codes
- [ ] Environment variable configuration
- [ ] Claude Desktop config example
- [ ] MCP inspector testing
- [ ] Unit tests for handlers
- [ ] README with setup instructions


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

