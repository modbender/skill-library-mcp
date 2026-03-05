---
name: openclaw-mobile-app-builder
description: Build and maintain mobile applications end-to-end with OpenClaw, including requirement shaping, architecture, implementation, debugging, testing, and release readiness. Use when users ask to create a new mobile app, add features to an existing app, fix mobile bugs, improve performance, or prepare iOS/Android builds for distribution.
---

# OpenClaw Mobile App Builder

## Core Operating Rules

- Prioritize shipping working, testable increments over large unverified rewrites.
- Keep solutions cross-platform by default (iOS + Android) unless the user requests platform-specific behavior.
- Reuse existing project patterns before introducing new abstractions.
- Prefer readable, strongly typed code and small, composable modules.
- Validate changes with commands the user can run locally.

## Standard Workflow

### 1) Clarify Scope

- Capture the user goal as a concrete deliverable.
- Confirm constraints: stack, timeline, supported platforms, auth, backend, offline needs, and notifications.
- Convert ambiguous requests into explicit acceptance criteria.

### 2) Detect Project Mode

- Detect whether this is:
1. a greenfield app,
2. a feature addition,
3. a bugfix,
4. a refactor/performance pass,
5. release hardening.
- Tailor the implementation depth to the detected mode.

### 3) Plan Before Editing

- Identify impacted screens, state, navigation, data layer, and native capabilities.
- Define the smallest safe implementation slice.
- List verification commands before coding.

### 4) Implement Incrementally

- Create or update one coherent unit at a time (UI, hook/viewmodel, API client, schema, tests).
- Keep business logic out of view layers where possible.
- Avoid introducing unused dependencies.

### 5) Validate and Report

- Run relevant checks (typecheck, lint, tests, build/start commands).
- Report what passed, what failed, and what was not run.
- Summarize changed files and key behavior updates.

## Technical Defaults

- Default stack: React Native + Expo + TypeScript.
- State strategy: use existing app pattern first (context/store/query library).
- Networking: typed API client boundaries and defensive parsing.
- Forms: explicit validation and clear user error states.
- Navigation: preserve current routing conventions.
- Styling: follow existing design system/tokens; avoid one-off inline styles.

## Mobile Quality Checklist

- Confirm loading, empty, success, and error states exist.
- Confirm touch targets are usable and layout adapts to small screens.
- Confirm text wraps correctly and avoids clipped content.
- Confirm accessibility labels/roles on interactive elements.
- Confirm no crashes from undefined/null edge cases.
- Confirm async actions have visible progress and failure handling.

## Performance Checklist

- Minimize unnecessary re-renders in lists and heavy screens.
- Memoize expensive derived values when profiling shows need.
- Keep bundle impact low; remove dead imports.
- Defer non-critical work from initial screen render.

## Data and API Rules

- Treat API contracts as versioned interfaces.
- Avoid breaking existing clients without a migration path.
- Add backward-compatible fields/functions when behavior changes.
- Keep serialization/deserialization logic centralized.

## Native/Release Readiness

- Verify app config, permissions, deep links, and environment variables.
- Ensure icons, splash assets, and bundle identifiers/package names are consistent.
- Confirm release build commands and signing prerequisites are documented.
- Provide a short release checklist for iOS and Android when requested.

## Debugging Protocol

- Reproduce first with clear steps.
- Isolate whether issue is UI, state, network, storage, or native bridge.
- Add narrow instrumentation/logging only where needed.
- Fix root cause, then remove temporary debugging noise.
- Add regression coverage for high-risk bugs.

## Output Contract

For each completed task, provide:

1. What changed.
2. Why the approach was chosen.
3. Exact files touched.
4. Validation commands run and outcomes.
5. Remaining risks or follow-ups.

## Guardrails

- Do not fabricate API responses, device behavior, or test results.
- Do not claim a task is complete without verification evidence.
- Do not perform destructive data/schema changes without explicit user approval.
- Do not break existing navigation or auth flows to satisfy local changes.

## Fast Paths

### Greenfield MVP

- Scaffold app shell.
- Implement core navigation and one vertical feature slice.
- Add typed API boundary and mock/real data switch.
- Add baseline test and lint/typecheck pass.

### Feature Addition

- Reuse existing screen/module pattern.
- Add minimal data contract changes.
- Add/adjust tests for new behavior.

### Bugfix

- Write reproduction notes.
- Fix smallest root cause.
- Add regression test if feasible.

