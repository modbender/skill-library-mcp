# CC_GodMode Workflows

Detailed documentation of all 7 standard workflows.

## Table of Contents

1. [New Feature](#1-new-feature)
2. [Bug Fix](#2-bug-fix)
3. [API Change](#3-api-change)
4. [Refactoring](#4-refactoring)
5. [Release](#5-release)
6. [Process Issue](#6-process-issue)
7. [Research Task](#7-research-task)

---

## 1. New Feature

**Trigger:** `New Feature: [description]`

### Flow
```
                                          ┌──▶ @validator ──┐
User ──▶ (@researcher)* ──▶ @architect ──▶ @builder              ├──▶ @scribe
                                          └──▶ @tester   ──┘
                                               (PARALLEL)
```

### Steps

1. **@researcher** (optional) - If new technology research is needed
   - Evaluates technologies
   - Finds best practices
   - Creates research report

2. **@architect** - Design phase
   - Analyzes requirements
   - Creates module structure
   - Documents trade-offs
   - Produces architecture decision

3. **@builder** - Implementation
   - Implements types first
   - Then backend (if needed)
   - Then frontend
   - Writes tests

4. **@validator + @tester** (parallel)
   - @validator: TypeScript, unit tests, security
   - @tester: E2E, screenshots, a11y, performance

5. **@scribe** - Documentation
   - Updates VERSION
   - Updates CHANGELOG
   - Updates README if needed

### Example

```
User: "New Feature: Add dark mode toggle to settings page"

Orchestrator:
→ @architect: Design state management for theme, component structure
→ @builder: Implement ThemeContext, SettingsToggle component
→ @validator: Verify TypeScript, run unit tests
→ @tester: Screenshot dark/light modes at 3 viewports
→ @scribe: Update CHANGELOG with dark mode feature
```

---

## 2. Bug Fix

**Trigger:** `Bug Fix: [description]`

### Flow
```
                ┌──▶ @validator ──┐
User ──▶ @builder                  ├──▶ (done)
                └──▶ @tester   ──┘
                     (PARALLEL)
```

### Steps

1. **@builder** - Fix implementation
   - Locate bug
   - Implement fix
   - Add regression test

2. **@validator + @tester** (parallel)
   - Verify fix doesn't break anything
   - Run relevant E2E tests

### Example

```
User: "Bug Fix: Login button not responding on mobile"

Orchestrator:
→ @builder: Fix click handler, add touch event support
→ @validator: Run existing tests
→ @tester: Test login flow on mobile viewport
```

---

## 3. API Change

**Trigger:** `API Change: [description]`

### Flow
```
                                                              ┌──▶ @validator ──┐
User ──▶ (@researcher)* ──▶ @architect ──▶ @api-guardian ──▶ @builder              ├──▶ @scribe
                                                              └──▶ @tester   ──┘
                                                                   (PARALLEL)
```

### Steps

1. **@architect** - Design API change
   - Define new schema
   - Plan migration

2. **@api-guardian** - Impact analysis (MANDATORY!)
   - Find ALL consumers
   - Classify breaking changes
   - Create migration checklist

3. **@builder** - Implement with consumer updates
   - Update API/types first
   - Update ALL consumers from checklist

4. **@validator + @tester** (parallel)
   - Verify ALL consumers updated
   - Test API endpoints

5. **@scribe** - Document breaking changes
   - Add breaking change section to CHANGELOG
   - Update API_CONSUMERS.md

### Critical Paths

These file patterns trigger @api-guardian:

- `src/api/**`
- `backend/routes/**`
- `shared/types/**`
- `types/`
- `*.d.ts`
- `openapi.yaml` / `openapi.json`
- `schema.graphql`

### Example

```
User: "API Change: Rename User.email to User.emailAddress"

Orchestrator:
→ @architect: Plan schema migration
→ @api-guardian: Find 5 consumers, mark as BREAKING
→ @builder: Update type + all 5 consumer files
→ @validator: Verify all imports correct, TypeScript passes
→ @tester: Test user-related flows
→ @scribe: Document breaking change, update API_CONSUMERS.md
```

---

## 4. Refactoring

**Trigger:** `Refactor: [description]`

### Flow
```
                            ┌──▶ @validator ──┐
User ──▶ @architect ──▶ @builder              ├──▶ (done)
                            └──▶ @tester   ──┘
                                 (PARALLEL)
```

### Steps

1. **@architect** - Plan refactoring
   - Analyze current structure
   - Design improved structure
   - Document affected modules

2. **@builder** - Execute refactoring
   - Move/rename files
   - Update imports
   - Keep tests passing

3. **@validator + @tester** (parallel)
   - Verify behavior unchanged
   - No regressions

---

## 5. Release

**Trigger:** `Prepare Release`

### Flow
```
User ──▶ @scribe ──▶ @github-manager
```

### Steps

1. **@scribe** - Prepare release
   - Finalize VERSION
   - Complete CHANGELOG
   - Update README

2. **@github-manager** - Publish
   - Create git tag
   - Create GitHub release
   - Trigger CI/CD

---

## 6. Process Issue

**Trigger:** `Process Issue #X`

### Flow
```
User: "Process Issue #X"
  │
  ▼
@github-manager loads Issue
  │
  ▼
Orchestrator analyzes: Type, Complexity, Areas
  │
  ▼
Appropriate workflow is executed
  │
  ▼
@github-manager creates PR with "Fixes #X"
```

### Issue Classification

| Type | Workflow |
|------|----------|
| Bug | Bug Fix workflow |
| Feature | New Feature workflow |
| Enhancement | Refactoring or Feature workflow |
| Documentation | @scribe only |

---

## 7. Research Task

**Trigger:** `Research: [topic]`

### Flow
```
User: "Research [topic]"
  │
  ▼
@researcher gathers knowledge
  │
  ▼
Report with findings + sources
```

### Steps

1. **@researcher** - Gather knowledge
   - WebSearch for current info
   - WebFetch documentation
   - Compare alternatives
   - Check security advisories

2. **Report** - Actionable findings
   - Key findings with sources
   - Recommendation
   - Next steps

### Example

```
User: "Research: Best state management for React in 2026"

@researcher:
→ Search: "React state management comparison 2026"
→ Fetch: Official docs for Zustand, Jotai, Redux
→ Compare: Bundle size, learning curve, performance
→ Report: Recommend Zustand for this project size
```

---

## Parallel Quality Gates

All workflows (except Release and Research) end with parallel quality gates:

```
                    ┌────────────────────┐
                    │      @builder      │
                    └─────────┬──────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               │               ▼
    ┌─────────────────┐       │     ┌─────────────────┐
    │   @validator    │       │     │    @tester      │
    │ (Code Quality)  │       │     │  (UX Quality)   │
    └────────┬────────┘       │     └────────┬────────┘
              │               │               │
              └───────────────┼───────────────┘
                              │
                        SYNC POINT
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
              BOTH PASS            ANY FAIL
                    │                   │
                    ▼                   ▼
               @scribe             @builder
                                   (fix it)
```

**Performance:** 40% faster than sequential execution!
