# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [PR-9](https://github.com/jgeofil/agent-skills/pull/9) - 2026-10-29

### Summary
Audited all 8 agent roles in `skills/development-roles/` to eliminate duplicate and overlapping skills, flattened nested plugin containers into standardized skill directories, unswapped inverted API definitions, and optimized progressive disclosure across all skills.

### Added
- Added unified architecture skills `skills/development-roles/architecture-swe/event-sourcing-cqrs/` and `skills/development-roles/architecture-swe/workflow-orchestration/`.
- Added standardized `skills/development-roles/architecture-swe/deployment-validation/SKILL.md` with schema-driven validation and cloud architecture references.
- Added standardized `skills/development-roles/ci-cd-swe/deployment-strategies/SKILL.md` covering zero-downtime, progressive delivery, and GitOps rollouts.
- Added standardized `skills/development-roles/data-scientist/data-pipeline-architecture/SKILL.md` unifying batch, streaming, and Medallion architecture patterns.
- Added progressive disclosure reference guides in `references/implementation-guide.md` across all monolithic skills (>350 lines).

### Fixed
- Fixed swapped skill files between `skills/development-roles/backend-swe/api-contract-normalizer/` and `skills/development-roles/backend-swe/api-endpoint-generator/`.
- Fixed non-standard stub skills (`skills/development-roles/maintenance-swe/explaining-code/`, `skills/development-roles/frontend-swe/state-ux-flow-builder/`, `skills/development-roles/frontend-swe/frontend-refactor-planner/`, and `skills/development-roles/frontend-swe/animation-micro-interaction-pack/`) with complete YAML frontmatter, pedagogical workflows, and implementation matrices.

### Changed
- Standardized YAML frontmatter across all 111 skills (`name`, `description`, `license: MIT`, `metadata: { version: "1.0", category: "<role>" }`), achieving 100% pass rate with zero errors and zero warnings on `skills/development/pr-review/scripts/validate_skills.py`.
- Promoted 10 Python backend skills from `skills/development-roles/backend-swe/python-development/skills/` directly to `skills/development-roles/backend-swe/`.
- Promoted 3 shell scripting skills from `skills/development-roles/ci-cd-swe/shell-scripting/skills/` directly to `skills/development-roles/ci-cd-swe/`.
- Promoted `skills/development-roles/db-management-swe/database-design/skills/postgresql-table-design/` to `skills/development-roles/db-management-swe/postgresql-table-design/`.
- Promoted `api-design-principles`, `architecture-patterns`, and `microservices-patterns` from `system-architecture/skills/` to top-level `skills/development-roles/architecture-swe/`.

### Removed
- Removed empty directory `skills/development-roles/ci-cd-swe/cicd-automation/`.
- Removed redundant overlapping skills in `skills/development-roles/ai-engineering-swe/`: merged `agent-orchestration-planner` into `ai-agent-orchestrator`, `langchain-workflow-builder` into `langchain-architecture`, `rag-pipeline-builder` into `rag-implementation`, `embedding-pipeline-builder` into `embedding-strategies`, `evaluation-harness` into `llm-evaluation`, and `prompt-template-builder` into `prompt-engineering-patterns`.
- Removed overlapping background job skills in `skills/development-roles/backend-swe/`: merged `background-jobs-designer` and `python-background-jobs` into `queue-job-processor`.
- Removed obsolete plugin containers: `system-architecture`, `python-development`, `shell-scripting`, `git-pr-workflows`, `data-engineering`, and `database-design`.
