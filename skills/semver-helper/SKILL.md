---
name: semver-helper
description: Semantic Versioning 2.0.0 reference guide. Quick decision trees and examples for choosing MAJOR, MINOR, or PATCH version bumps.
author: Gelmir
tags: [semver, versioning, release]
---

# Semver Helper

Quick reference for Semantic Versioning 2.0.0 decisions.

## The Golden Rule

Given version `MAJOR.MINOR.PATCH`, increment:

| Level | Bump When | Reset Lower? |
|-------|-----------|--------------|
| **MAJOR** (X.0.0) | Breaking changes (incompatible API changes) | Yes, MINOR and PATCH → 0 |
| **MINOR** (0.X.0) | New features (backwards compatible) | Yes, PATCH → 0 |
| **PATCH** (0.0.X) | Bug fixes (backwards compatible) | No |

## Quick Decision Tree

```
Did you change anything users depend on?
├─ No (internal only) → PATCH
└─ Yes
   └─ Did you remove/change existing behavior?
      ├─ Yes → MAJOR
      └─ No (only added new stuff)
         └─ Is the new stuff visible to users?
            ├─ Yes → MINOR
            └─ No → PATCH
```

## Real Examples

### 🔴 MAJOR (Breaking)

- Remove a function, endpoint, or CLI flag
- Change the return type of a function
- Require a new mandatory parameter
- Change default behavior significantly
- Rename something users depend on
- Upgrade a dependency that forces downstream changes

**Examples:**
- `removeUser()` → `deleteUser()` rename
- API response format changed from `{id: 1}` to `{data: {id: 1}}`
- Dropping support for Node 16 (if users must upgrade)

### 🟡 MINOR (Feature)

- Add new functionality
- Add optional parameters
- Add new exports/exports
- Deprecate old features (warn, don't remove)
- Performance improvements (no API change)

**Examples:**
- Add `createUser()` alongside existing user functions
- Add `--format json` flag to CLI
- Add new event listeners/hooks
- Mark old method as deprecated (still works)

### 🟢 PATCH (Fix)

- Fix bugs without changing intended behavior
- Documentation updates
- Internal refactoring (no visible change)
- Dependency updates (no API change)
- Test additions

**Examples:**
- Fix null pointer exception
- Correct typo in error message
- Fix race condition
- Update README

## Version Progression Examples

| Changes | Version Bump |
|---------|--------------|
| `fix: null pointer` | `1.2.3` → `1.2.4` |
| `feat: add auth` | `1.2.3` → `1.3.0` |
| `breaking: remove old API` | `1.2.3` → `2.0.0` |
| `fix: bug + feat: new thing` | `1.2.3` → `1.3.0` (MINOR wins) |
| `fix: bug + breaking: remove API` | `1.2.3` → `2.0.0` (MAJOR wins) |

## Pre-releases

Use suffixes for testing before stable:

- `2.0.0-alpha.1` — Very early, unstable
- `2.0.0-beta.2` — Feature complete, testing
- `2.0.0-rc.1` — Release candidate, final testing

Pre-releases sort before their stable version:
`1.0.0-alpha < 1.0.0-beta < 1.0.0-rc < 1.0.0`

## Common Edge Cases

| Situation | Bump | Why |
|-----------|------|-----|
| Fix a bug that was introduced *this version* | PATCH | Still a fix |
| Deprecate a feature (but keep it working) | MINOR | New "deprecated" state is info |
| Change undocumented/internal behavior | PATCH | Users shouldn't depend on it |
| Security fix that requires API change | MAJOR | Breaking for security |
| Rewriting internals, same behavior | PATCH | Invisible to users |
| Adding tests/docs only | PATCH | No code change |

## Anti-Patterns

❌ **Don't** bump MAJOR for big new features (unless breaking)
❌ **Don't** bump MINOR for bug fixes
❌ **Don't** bump PATCH for new functionality
❌ **Don't** keep old numbers when bumping: `1.2.3 → 2.2.3` is wrong

## Cheat Sheet

```
Users' code breaks? → MAJOR
Users get new toys? → MINOR
Users get fixes? → PATCH
```
