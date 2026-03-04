---
name: Apple Maps (MacOS)
slug: apple-maps
version: 1.0.0
homepage: https://clawic.com/skills/apple-maps
description: Search places, open routes, and run Apple Maps workflows on macOS using local CLI commands and shortcut automation with explicit safety checks.
changelog: Initial release with deterministic Apple Maps URL workflows, shortcuts CLI fallback, and confirmation gates for high-impact actions.
metadata: {"clawdbot":{"emoji":"🗺️","requires":{"bins":[],"anyBins":["open","shortcuts","osascript"],"config":["~/apple-maps/"]},"os":["darwin"],"configPaths":["~/apple-maps/"]}}
---

## Setup

On first use, follow `setup.md` to establish scope, preferred command path, and safety defaults before routing or sharing actions.

## When to Use

User wants to search places, categories, addresses, and routes in Apple Maps from macOS without browser-first workflows.
Agent handles place search, nearby category lookup, route launching, and reusable map-link generation.

## Requirements

- macOS with Maps.app installed.
- At least one working command path: `open`, `shortcuts`, or `osascript` fallback.
- Network access to Apple Maps for live place and route results.
- Explicit confirmation before sharing links externally or launching bulk actions.

## Architecture

Memory lives in `~/apple-maps/`. See `memory-template.md` for structure.

```text
~/apple-maps/
├── memory.md             # Status, defaults, and validated command path
├── command-paths.md      # Command priority, probes, and URL strategy
├── safety-log.md         # Confirmations for high-impact actions
└── operation-log.md      # Search and route operation IDs with outcomes
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup and first-run behavior | `setup.md` |
| Memory structure | `memory-template.md` |
| Command hierarchy and probes | `command-paths.md` |
| Deterministic operation flows | `operation-patterns.md` |
| Safety checklist before action | `safety-checklist.md` |
| Failure handling and recovery | `troubleshooting.md` |

## Data Storage

All skill files are stored in `~/apple-maps/`.
Before creating or changing local files, describe the planned write and ask for confirmation.

## Core Rules

### 1. Use Apple Maps URL Workflows as Primary Interface
- Build map requests as explicit Apple Maps URLs and launch with `open -a Maps`.
- Prefer documented URL parameters instead of UI-only automation.

### 2. Probe Command Path Before Operations
- Verify command availability in strict order: `open`, `shortcuts`, `osascript`.
- If only fallback paths are available, explain capability limits before executing.

### 3. Keep Searches Bounded and Deterministic
- Require clear intent: query text, optional area, and optional map zoom/context.
- For ambiguous requests like "best restaurants", ask for location context before launching Maps.

### 4. Preview Generated URL Before Execution
- For every action, show the final URL and explain major parameters.
- If the query contains user-sensitive text, confirm before opening or sharing.

### 5. Confirm High-Impact Actions
- Require explicit confirmation for route launches with destination changes, share-link generation, and repeated bulk opens.
- For repeated actions, present a count and require a second confirmation.

### 6. Verify Result State After Launch
- After opening Maps, summarize expected visible outcome (query, destination, mode).
- If result does not match intent, refine parameters instead of retrying blindly.

### 7. Minimize Data Exposure
- Use minimal query strings needed for the requested task.
- Do not send map queries to undeclared third-party APIs.

## Common Traps

- Launching vague searches without area context -> noisy, low-value results.
- Sharing raw links that include private notes -> accidental disclosure.
- Using UI scripting as default path -> brittle behavior across locales.
- Opening many candidate links at once -> user loses context quickly.
- Assuming route mode without confirmation -> wrong transport directions.

## External Endpoints

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| https://maps.apple.com | Search text, optional coordinates, routing parameters | Retrieve map, place, and route results in Apple Maps |

No other external endpoint is required by default.

## Security & Privacy

**Data that stays local:**
- Operational defaults, safety choices, and command reliability notes in `~/apple-maps/`.

**Data that may leave your machine:**
- Place queries, route origins/destinations, and map parameters sent to Apple Maps when opening URLs.

**This skill does NOT:**
- Execute undeclared API calls.
- Persist sensitive location context without user approval.
- Run bulk opens or share actions without explicit confirmation.

## Trust

By using this skill, map queries and route parameters are sent to Apple Maps.
Only use this workflow if you trust Apple Maps with that data.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `macos` - macOS command workflows and automation patterns.
- `travel` - travel-planning flows and destination strategy.
- `restaurants` - food venue discovery and shortlist workflows.
- `car-rental` - route-linked transport planning.

## Feedback

- If useful: `clawhub star apple-maps`
- Stay updated: `clawhub sync`
