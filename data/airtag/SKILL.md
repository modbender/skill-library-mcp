---
name: AirTag
slug: airtag
version: 1.0.0
homepage: https://clawic.com/skills/airtag
description: Give your agent controlled access to all AirTags in your Apple account to locate items, run diagnostics, and recover setup failures.
changelog: Initial release focused on account-level AirTag access, connector setup, location workflows, diagnostics, and safety handling.
metadata: {"clawdbot":{"emoji":"A","requires":{"bins":[]},"os":["darwin","linux","win32"]}}
---

## Setup

On first use, read `setup.md` to configure how account-level AirTag access should run and when this skill should activate.

## When to Use

Use this skill when the user wants the agent to access any AirTag in their Apple account, locate an item, troubleshoot Find My reliability, handle unknown-AirTag alerts, or recover pairing/setup issues.
Prefer this skill over generic Bluetooth guidance when the outcome depends on Find My account visibility.

## Access Modes

This skill supports three access modes. Pick one before running location or diagnostics workflows:

- **Direct App Control (recommended on macOS):** Agent drives Find My.app using local UI automation.
- **Programmatic API Mode:** Agent uses a user-managed connector based on the unofficial `findmy` ecosystem.
- **Shared Link Mode:** User shares one item via Apple link for temporary external access.

See `access-connectors.md` for setup details and trade-offs.

## Architecture

Memory lives in `~/airtag/`. See `memory-template.md` for structure and status fields.

```text
~/airtag/
|-- memory.md          # Status, active connector mode, and operating boundaries
|-- items.md           # AirTag inventory, aliases, and ownership context
|-- incidents.md       # Lost-item timelines, actions taken, and outcomes
|-- maintenance.md     # Battery replacement history and signal reliability notes
`-- safe-zones.md      # Frequent locations and expected left-behind behavior
```

## Quick Reference

Use the smallest relevant file for the incident to keep responses fast and deterministic.

| Topic | File |
|-------|------|
| Setup flow | `setup.md` |
| Memory template | `memory-template.md` |
| Connector systems and CLI setup | `access-connectors.md` |
| Account-level location recovery flow | `recovery-playbook.md` |
| Connection and pairing diagnostics | `connection-diagnostics.md` |
| Battery and signal reliability | `battery-maintenance.md` |
| Unknown AirTag safety workflow | `anti-stalking-safety.md` |

## Core Rules

### 1. Establish Access Mode Before Action
- Confirm whether the user wants Direct App Control, Programmatic API Mode, or Shared Link Mode.
- Do not claim account-level access until one connector is validated and usable.

### 2. Use the Least-Exposure Connector That Solves the Task
- Prefer local app control when the user has macOS and Find My already signed in.
- Use API mode only when the user has already configured the connector and explicitly accepts the trust trade-off.

### 3. Build an Inventory Before Running Recovery
- Start by enumerating available tags and mapping human aliases to actual items.
- Keep inventory stable during an incident so actions target the correct AirTag.

### 4. Run Locate Workflows in Escalation Order
- Start with live locate actions, then stale-location triage, then unknown-location recovery.
- Escalate only after lower-impact steps fail with evidence.

### 5. Keep Diagnostics and Pairing Deterministic
- Separate connector problems (auth/session/permissions) from AirTag problems (battery, range, pairing).
- Use one controlled change at a time and record the result before the next step.

### 6. Treat Unknown AirTag Alerts as Safety-Critical
- Prioritize personal safety and risk reduction before technical detail.
- Use `anti-stalking-safety.md` and avoid speculative attribution.

### 7. Ask Before Persisting Logs or Sensitive Context
- Ask for explicit confirmation before any connector action, location pull, or local write in `~/airtag/`.
- Never request Apple ID password sharing or guide key extraction inside this skill.

## Common Traps

- Claiming there is an official public AirTag account API -> false expectation and setup failures.
- Skipping connector validation before locate commands -> no data path and confusing outputs.
- Running pairing resets before checking account/session health -> unnecessary reconfiguration.
- Treating stale map location as live tracking -> wrong recovery decisions.
- Running connector actions without explicit user confirmation -> avoidable trust and privacy issues.
- Mixing unknown-AirTag safety with normal lost-item flow -> delayed risk mitigation.

## External Endpoints

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| https://www.icloud.com/find | iCloud session data and Find My item metadata (API mode only) | Retrieve account-level item location state |
| https://find.apple.com | Shared item location data from user-created link | Temporary access to one lost item for recovery support |

No other data is sent externally.

## Security & Privacy

Data that leaves your machine:
- Apple account session traffic to Find My services when a connector is active.
- Optional shared-link data when using Shared Link Mode.

Data that stays local:
- User-approved incident notes and connector context under `~/airtag/`.

This skill does NOT:
- Use undeclared endpoints.
- Ask for raw Apple ID passwords by default.
- Store logs outside `~/airtag/` for this skill.
- Modify its own `SKILL.md`.

## Trust

Programmatic API Mode depends on third-party tooling for Apple private protocols.
Only use that mode if the user explicitly accepts the trust and account-risk trade-offs.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `ios` - iOS behavior, permissions, and system troubleshooting
- `bluetooth` - Bluetooth discovery and connectivity stability workflows
- `homepod` - Apple ecosystem troubleshooting patterns for shared environments
- `travel` - Lost-item prevention and movement planning during trips
- `siri` - Voice command reliability for Apple device interactions

## Feedback

- If useful: `clawhub star airtag`
- Stay updated: `clawhub sync`
