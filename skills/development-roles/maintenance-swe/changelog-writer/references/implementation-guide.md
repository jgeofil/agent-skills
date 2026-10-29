# Changelog & Release Notes Writer - Implementation Guide & Code Recipes

## [2.1.0] - 2024-01-15

### Added

- OAuth2 authentication support
- User profile management API
- Dark mode toggle

### Changed

- Improved error messages
- Updated dependencies to latest versions

### Deprecated

- Legacy authentication method (will be removed in 3.0.0)

### Fixed

- Memory leak in WebSocket connection
- Incorrect date formatting in reports
- Race condition in concurrent requests

### Security

- Patched XSS vulnerability in user input

## [2.0.0] - 2023-12-01

### Breaking Changes

- ⚠️ Removed support for Node.js 16
- ⚠️ Changed API response format for `/users` endpoint
- ⚠️ Renamed `config.yaml` to `config.yml`

### Added

- Complete API rewrite with improved performance
- WebSocket support for real-time updates

### Migration Guide

See [MIGRATION_v2.md](./docs/MIGRATION_v2.md) for upgrade instructions.

[unreleased]: https://github.com/user/project/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/user/project/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/user/project/releases/tag/v2.0.0
```

## Release Notes Format

````markdown
# Release v2.1.0 - "Feature Release Name"

Released: January 15, 2024

## 🎉 Highlights

This release brings major improvements to authentication and user experience:

- **OAuth2 Support**: Users can now sign in with Google, GitHub, and Microsoft
- **Dark Mode**: Toggle between light and dark themes
- **Performance**: 40% faster API response times

## ✨ New Features

- OAuth2 authentication with popular providers (#456)
- User profile management API (#478)
- Dark mode toggle in settings (#492)
- Export data in CSV format (#501)

## 🐛 Bug Fixes

- Fixed memory leak in WebSocket connections (#489)
- Resolved incorrect date formatting in reports (#495)
- Fixed race condition in concurrent API requests (#503)

## 🔄 Changes

- Improved error messages across the application
- Updated all dependencies to latest stable versions
- Refined UI animations for smoother experience

## 🔒 Security

- Patched XSS vulnerability in user input validation
- Updated JWT library to address CVE-2024-1234

## 📚 Documentation

- Added OAuth2 setup guide
- Updated API reference with new endpoints
- Improved troubleshooting section

## 🙏 Contributors

Thank you to all contributors who made this release possible:

- @alice - OAuth2 implementation
- @bob - Dark mode feature
- @charlie - Bug fixes and testing

## 📦 Installation

```bash
npm install project-name@2.1.0
# or
yarn add project-name@2.1.0
```
````

## 🔗 Links

- [Full Changelog](https://github.com/user/project/compare/v2.0.0...v2.1.0)
- [Documentation](https://docs.projectname.com)
- [Migration Guide](./docs/MIGRATION_v2.md)

---

**Note:** This is a minor release. No breaking changes. Safe to upgrade from 2.0.x.

````

## Semantic Versioning Rules

Given a version number MAJOR.MINOR.PATCH (e.g., 2.1.0):

1. **MAJOR** (2.x.x → 3.x.x)
   - Breaking changes
   - Incompatible API changes
   - Removed features

2. **MINOR** (2.1.x → 2.2.x)
   - New features
   - Backward-compatible functionality
   - Deprecated features

3. **PATCH** (2.1.0 → 2.1.1)
   - Bug fixes
   - Security patches
   - Performance improvements

**Special versions:**
- `0.x.x` - Initial development (breaking changes allowed in minor)
- `x.y.0-alpha.1` - Pre-release
- `x.y.0-beta.2` - Beta release
- `x.y.0-rc.1` - Release candidate

## Git Commands for Changelog Generation

```bash
# Get commits since last tag
git log $(git describe --tags --abbrev=0)..HEAD --oneline

# Get commits between two tags
git log v2.0.0..v2.1.0 --oneline

# Get commits with PR numbers
git log --merges --pretty=format:"%s" v2.0.0..HEAD

# Get contributors
git log v2.0.0..HEAD --format='%aN' | sort -u

# Get commit count by type
git log v2.0.0..HEAD --oneline | grep -E '^[a-f0-9]+ (feat|fix|docs)' | cut -d' ' -f2 | sort | uniq -c
````

## Breaking Changes Detection

Look for these indicators:

- Commit message contains `BREAKING CHANGE:`
- Commit type has `!` (e.g., `feat!:`)
- PR labeled with "breaking-change"
- Major dependency updates
- API endpoint changes
- Config file format changes

**Document clearly:**

````markdown
### Breaking Changes

⚠️ **API Response Format Changed**

The `/api/users` endpoint now returns:

```json
// Before
{ "data": [...] }

// After
{ "users": [...], "total": 100 }
```
````

**Migration:** Update your API client to access `users` instead of `data`.

````

## Automation Tools

### Using conventional-changelog
```bash
npm install -g conventional-changelog-cli

# Generate changelog
conventional-changelog -p angular -i CHANGELOG.md -s

# Generate for specific version
conventional-changelog -p angular -i CHANGELOG.md -s -r 0
````

### Using git-cliff

```bash
# Install git-cliff
cargo install git-cliff

# Generate changelog
git-cliff --tag v2.1.0 > CHANGELOG.md

# Generate release notes
git-cliff --tag v2.1.0 --unreleased
```

### GitHub Release Script

```bash
#!/bin/bash
# scripts/release.sh

VERSION=$1
PREVIOUS_TAG=$(git describe --tags --abbrev=0)

# Generate release notes
gh release create "$VERSION" \
  --title "Release $VERSION" \
  --notes "$(git log $PREVIOUS_TAG..HEAD --pretty=format:'- %s')"
```

## User-Facing vs Developer-Facing

### User-Facing (Release Notes)

- Focus on benefits and features
- Less technical jargon
- Include screenshots/demos
- Highlight user experience improvements
- Provide upgrade instructions

### Developer-Facing (Changelog)

- Technical details
- API changes
- Breaking changes with migration guides
- Dependencies updates
- Internal refactorings

## Templates by Project Type

### Library/Package

Focus on: API changes, breaking changes, new methods

### Application

Focus on: New features, bug fixes, UI improvements

### CLI Tool

Focus on: New commands, flag changes, behavior changes

### API Service

Focus on: Endpoint changes, performance, security
