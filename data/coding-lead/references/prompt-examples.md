# Prompt Examples

Real examples for spawning Claude Code with different task types.

## Example 1: Simple Bug Fix (agent does directly)

Task: "Fix the date format in UserProfile.tsx"
Classification: Simple (single file, <60 lines)
Action: Agent reads file, edits directly, logs to memory.

## Example 2: Medium Feature (spawn Claude Code)

Prompt to Claude Code:

```
## Project
- Path: /path/to/my-laravel-app
- Stack: Laravel 10 + React 18 + TypeScript + Inertia.js
- Architecture: Action-based (not Service layer), Controllers under 20 lines

## Coding Standards
- KISS + SOLID + DRY
- Action pattern for business logic (one Action = one operation)
- FormRequest for validation, Policy for authorization
- Methods <200 lines, follow existing code style
- Comments where helpful
- Clear commit message

## Historical Context
- 2026-02-20: Switched from Service to Action pattern for all new features
- 2026-02-25: common/ module has auth system, reuse CommonAuthTrait
- Known: PlatformLink has 6 types, use enum not magic strings

## Task
Add a "favorites" feature: users can favorite items.
Need: migration, model, action, controller, API resource, React component.

## Acceptance Criteria
- [ ] Migration creates user_favorites pivot table
- [ ] Action handles add/remove/check
- [ ] Controller under 20 lines, delegates to Action
- [ ] React component with optimistic update
- [ ] Uses existing auth system from common/
- [ ] Existing tests pass
```

## Example 3: Complex Refactor (RESEARCH > PLAN > EXECUTE)

### Research prompt:

```
Investigate /path/to/my-app for refactoring the resource aggregation system.

DO NOT make changes. Only report:
1. All files in app/Services/Collectors/
2. How the Aggregator calls each collector
3. Error handling patterns used
4. Any code duplication between collectors
5. Test coverage for this module
```

### Execute prompt (after plan confirmed):

```
## Project
- Path: /path/to/my-app
- Focus: app/Services/Collectors/ and Aggregator.php

## Coding Standards
[same as above]

## Historical Context
- Research found: 3 collectors duplicate HTTP retry logic
- Plan approved: extract shared HttpClientTrait, refactor collectors to use it
- Confirmed: do NOT change the collector interface, only internal implementation

## Task
1. Create app/Traits/HttpClientTrait.php with shared retry/timeout logic
2. Refactor 3 collectors to use the trait
3. Keep Aggregator unchanged (interface preserved)
4. Run existing tests

## Acceptance Criteria
- [ ] HttpClientTrait extracted with configurable retry (default 3)
- [ ] All 3 collectors use trait, no duplicate HTTP logic
- [ ] Aggregator works unchanged
- [ ] Existing tests pass
- [ ] No new dependencies
```

## Example 4: Cross-Session Task

Session 1 ends with memory entry:
```
## favorites feature - day 1
- Created migration, model, action (backend done)
- React component started but not finished (FavoriteButton.tsx)
- Blocked: need to decide between Zustand and TanStack Query for optimistic update
- TODO: finish frontend, add tests
```

Session 2 agent reads this, spawns Claude Code with:
```
## Continuing: favorites feature (day 2)

Previous session completed backend (migration, model, action).
Frontend component started at FavoriteButton.tsx.
Open decision: use TanStack Query mutation for optimistic update (confirmed).

## Task
1. Complete FavoriteButton.tsx with TanStack Query optimistic mutation
2. Add toggle animation
3. Add to detail page
4. Write 2 unit tests for the Action
```