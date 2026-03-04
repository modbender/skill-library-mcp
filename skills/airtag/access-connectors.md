# Access Connectors - AirTag

Use this file to select and configure how the agent gets account-level AirTag access.

## Connector Matrix

| Mode | Best for | Platform | Trade-off |
|------|----------|----------|-----------|
| Direct App Control | Fastest practical control when Find My is already signed in | macOS | Requires UI automation permissions |
| Programmatic API Mode (`findmy`) | Scripted location/report workflows | Cross-platform after setup | Unofficial/private-protocol stack |
| Shared Link Mode (`find.apple.com`) | Temporary access to one lost item | Any | One item at a time, not full account inventory |

## 1) Direct App Control (Recommended on macOS)

Goal: let the agent operate Find My.app directly with local automation.

Requirements:
- macOS with Find My.app signed in
- Accessibility/Screen Recording permissions for the automation bridge
- A user-approved local automation bridge already configured

Use this mode when the user wants minimum credential exposure and direct control over all account-visible AirTags.

## 2) Programmatic API Mode (`findmy`)

Goal: use a Python-based toolchain for location reports and scripted operations.

Requirements:
- User-managed connector already configured outside this skill
- User-approved session/auth context already available

Known setup facts from the project docs:
- Location report fetching is supported in the ecosystem.
- These tools use private Apple protocols and should be treated as high-trust dependencies.
- This skill should not guide key extraction or credential handling.

Use this mode for deeper scripted workflows when the user explicitly accepts third-party private-protocol tooling.

## 3) Shared Link Mode (`find.apple.com`)

Goal: give temporary access for one lost item without granting full account automation.

Flow:
1. User shares item location from Find My.
2. Helper opens link on `find.apple.com`.
3. Helper can guide recovery and status checks for that item.

Use this mode when the user wants fast collaboration with minimal setup and limited scope.

## Mode Selection Rules

1. Prefer Direct App Control when macOS + Find My are already available.
2. Use Shared Link Mode for urgent one-item recovery with low setup overhead.
3. Use API Mode only when deterministic scripting is required and trust is explicit.
4. If no connector is ready, start with setup diagnostics from `connection-diagnostics.md`.
