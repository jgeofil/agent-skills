---
name: changelog-writer
description: >-
  Generates changelogs and release notes from git commits, PR titles, and issue references. Organizes changes by impact type (breaking, features, fixes, improvements), formats according to Keep a Changelog standard, and provides version tagging and semantic versioning suggestions. Use when users request "create changelog", "write release notes", "document version changes", or "prepare release".
license: MIT
metadata:
  version: "1.0"
  category: maintenance-swe
---

# Changelog & Release Notes Writer

Generate professional changelogs and release notes from version control history.

## Core Workflow

1. **Analyze commits**: Parse git history since last release
2. **Categorize changes**: Group by type (feat, fix, docs, etc.)
3. **Identify breaking changes**: Flag incompatible changes
4. **Extract highlights**: Surface most important changes
5. **Format document**: Follow Keep a Changelog format
6. **Suggest version**: Recommend semantic version bump
7. **Generate release notes**: Create user-friendly summary

## Commit Analysis

### Extract Information From

- Commit messages (preferably conventional commits)
- PR titles and descriptions
- Issue references (#123)
- Merge commit messages
- Commit authors

### Parse Patterns

```
feat(auth): add OAuth2 support
^    ^      ^
|    |      └─ Description
|    └─ Scope (optional)
└─ Type
```

**Types to Categories:**

- `feat` → Added
- `fix` → Fixed
- `docs` → Documentation
- `style`, `refactor` → Changed
- `perf` → Performance
- `test` → Testing
- `chore`, `ci` → Internal
- `BREAKING CHANGE` → Breaking Changes

## Changelog Format (Keep a Changelog)

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- New feature X
- Support for Y

### Changed

- Updated Z behavior

### Fixed

- Resolved issue #123

## Best Practices

1. **Be specific**: "Fixed login bug" → "Fixed session timeout on mobile"
2. **Link issues**: Reference GitHub issues (#123)
3. **Credit contributors**: Acknowledge work
4. **Highlight impact**: Mark breaking changes clearly
5. **Group logically**: By type, not chronologically
6. **Update regularly**: With each release
7. **Follow conventions**: Keep a Changelog format
8. **Semantic versioning**: Use correctly

## Changelog Entry Examples

### Good Examples

```markdown
### Added

- OAuth2 authentication support (#456) - @alice
- Export data in CSV format with custom column selection (#501)

### Fixed

- Resolved memory leak in WebSocket connections affecting long-running sessions (#489)
- Fixed race condition in concurrent API requests that caused data inconsistency (#503)
```

### Bad Examples

```markdown
### Added

- Added stuff
- New feature

### Fixed

- Fixed bug
- Updates
```

## Version Suggestion Algorithm

```
If breaking changes detected:
  MAJOR++, MINOR=0, PATCH=0
Else if new features:
  MINOR++, PATCH=0
Else if only fixes:
  PATCH++
```

## Release Checklist

Before publishing release:

- [ ] Review all commits since last release
- [ ] Identify breaking changes
- [ ] Categorize changes properly
- [ ] Update CHANGELOG.md
- [ ] Write release notes
- [ ] Update version in package.json/pyproject.toml
- [ ] Create git tag
- [ ] Push tag to trigger CI/CD
- [ ] Publish to package registry (npm, PyPI, etc.)
- [ ] Create GitHub release with notes
- [ ] Announce on relevant channels

## Output Checklist

Every changelog generation should provide:

- [ ] Formatted CHANGELOG.md following Keep a Changelog
- [ ] Release notes draft (user-friendly)
- [ ] Semantic version suggestion (X.Y.Z)
- [ ] Breaking changes clearly marked
- [ ] Migration guide for breaking changes
- [ ] Git tag command to run
- [ ] Links to compare view


## Reference Documentation

- [Implementation Guide](references/implementation-guide.md)

