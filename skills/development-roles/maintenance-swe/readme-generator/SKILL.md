---
name: readme-generator
description: >-
  Generates comprehensive README files with badges, installation, usage, API docs, and contribution guidelines. Use when users request "README", "project documentation", "readme template", "documentation generator", or "project setup docs".
license: MIT
metadata:
  version: "1.0"
  category: maintenance-swe
---

# README Generator

Create comprehensive, professional README documentation for projects.

## Core Workflow

1. **Analyze project**: Identify type and features
2. **Add header**: Title, badges, description
3. **Document setup**: Installation and configuration
4. **Show usage**: Examples and API
5. **Add guides**: Contributing, license
6. **Include extras**: Screenshots, roadmap

## README Template

```markdown
# Project Name

[![npm version](https://img.shields.io/npm/v/package-name.svg)](https://www.npmjs.com/package/package-name)
[![Build Status](https://github.com/username/repo/workflows/CI/badge.svg)](https://github.com/username/repo/actions)
[![Coverage](https://codecov.io/gh/username/repo/branch/main/graph/badge.svg)](https://codecov.io/gh/username/repo)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)

Brief description of what this project does and who it's for. One to two sentences that capture the essence of the project.

## Features

- ✨ Feature one with brief description
- 🚀 Feature two with brief description
- 🔒 Feature three with brief description
- 📦 Feature four with brief description

## Demo

![Demo GIF](https://example.com/demo.gif)

[Live Demo](https://demo.example.com) | [Documentation](https://docs.example.com)

## Quick Start

\`\`\`bash
npx create-project-name my-app
cd my-app
npm run dev
\`\`\`

## Installation

### Prerequisites

- Node.js 18.0 or higher
- npm 9.0 or higher (or pnpm/yarn)

### Package Manager

\`\`\`bash
# npm
npm install package-name

# pnpm
pnpm add package-name

# yarn
yarn add package-name
\`\`\`

### From Source

\`\`\`bash
git clone https://github.com/username/repo.git
cd repo
npm install
npm run build
\`\`\`

## Best Practices

1. **Start with value**: Lead with what the project does
2. **Quick start first**: Get users running quickly
3. **Show, don't tell**: Include code examples
4. **Keep updated**: Sync with code changes
5. **Use badges**: Show project health
6. **Add visuals**: Screenshots and diagrams
7. **Link related**: Connect to other docs
8. **Be consistent**: Follow established patterns

## Output Checklist

Every README should include:

- [ ] Project title and description
- [ ] Badges (build, version, license)
- [ ] Features list
- [ ] Quick start / Installation
- [ ] Usage examples
- [ ] API documentation
- [ ] Configuration options
- [ ] Contributing guidelines
- [ ] License information
- [ ] Support/contact info

## Operational Runbook Variant (Spec-First Alignment)

> [!NOTE]
> For backend services, CLI utilities, and repositories governed by **Spec-First Architecture (`spec-first-architect-v2`)**, `README.md` serves as a **Layer 5 Operational Runbook** rather than a consumer library page. Ensure it includes:
> - **Architecture Diagram:** Visual representation of cellular dependencies and I/O boundaries.
> - **Environment Variable Table:** Exhaustive list matching Layer 1 `contracts/main_contract` (variable name, type, default, required, and secret classification).
> - **Minimum IAM Permissions:** Exact cloud roles and permissions needed at runtime.
> - **Verification Commands:** Explicit CLI examples including `--dry-run` and `--once` execution.
> - **Zero-Inference Deployment:** Dockerfile and `docker-compose.yml` run instructions.

## Related Skills

- `spec-first-architect-v2` — Mandates Layer 5 Operational Runbook READMEs aligned with the Composition Root (`dist/main/`)
- `changelog-writer` — Maintaining structured release notes alongside README documentation


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

