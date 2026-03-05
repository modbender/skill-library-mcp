---
name: HomePod
slug: homepod
version: 1.0.0
homepage: https://clawic.com/skills/homepod
description: Set up, troubleshoot, and optimize HomePod and HomeKit audio workflows with reliable Siri control and room-aware playback tuning.
changelog: Initial release with HomePod setup, diagnostics, direct control workflows, and automation reliability guidance.
metadata: {"clawdbot":{"emoji":"H","requires":{"bins":[]},"os":["darwin","linux","win32"]}}
---

## Setup

On first use, read `setup.md` for activation preferences and baseline context.

## When to Use

Use this skill when tasks involve HomePod setup, direct playback control, Siri playback issues, Home app automations, or multiroom audio stability. Prefer this over generic audio advice when Apple Home ecosystem constraints drive the outcome.

## Architecture

Memory lives in `~/homepod/`. See `memory-template.md` for structure.

```text
~/homepod/
|-- memory.md              # Status, activation boundaries, and current setup
|-- homes.md               # Home topology and device mapping
|-- automation-log.md      # Trigger failures, fixes, and validation results
`-- network-notes.md       # Wi-Fi, Thread, and router behavior notes
```

## Quick Reference

Use the smallest relevant file for the current incident to keep troubleshooting focused.

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| Direct connection and control | `direct-control.md` |
| Network triage flow | `network-diagnostics.md` |
| Automation reliability playbook | `automation-playbook.md` |
| Siri failure recovery map | `siri-recovery.md` |

## Core Rules

### 1. Confirm Real Topology Before Advice
- Capture HomePod model, software version, home hub role, and active network layout before suggesting fixes.
- Do not assume Thread, stereo pairs, or eARC are available without explicit confirmation.

### 2. Separate Network, Device, and Service Failures
- Classify each incident as local network path, HomePod device state, or cloud service dependency.
- Apply the narrowest fix first and re-test before moving to broader resets.

### 3. Keep Automation Debugging Deterministic
- For each failing automation, log trigger, condition, expected action, and actual result in one record.
- Test one change at a time so root cause remains attributable.

### 4. Validate Multiroom Audio with Repeatable Checks
- Test sync, handoff, and output routing with a fixed sequence across all target rooms.
- Treat intermittent latency as a measurable defect, not user error.

### 5. Protect User Privacy and Household Boundaries
- Keep notes focused on devices, states, and failures, never on raw voice transcripts or personal content.
- If account-level actions are needed, explain impact and request explicit confirmation first.

### 6. Prefer Reversible Fixes Before Factory Reset
- Start with service restart, network path validation, and accessory reassociation before destructive actions.
- Reserve full reset workflows for verified dead-end states only.

### 7. Execute Direct Control in Guarded Mode
- For command execution, require explicit target and intent confirmation before any mutating action.
- Use `direct-control.md` and run read-only commands first (`scan`, `device_info`, `playing`, `volume`) before `play`, `pause`, `stop`, or `set_volume`.

## Common Traps

- Treating every Siri error as network related -> repeated failures because account or Home hub state was never checked.
- Resetting devices before collecting evidence -> no reproducible signal and slower recovery.
- Changing multiple automation variables at once -> unclear root cause and unstable behavior.
- Ignoring software version drift across devices -> non-deterministic automation and audio routing outcomes.
- Testing only one room in multiroom setups -> latent sync issues missed until production use.
- Sending control commands to ambiguous device names -> wrong-room playback changes and user trust loss.

## Security & Privacy

Data that leaves your machine:
- None by default. Direct control uses local network traffic to HomePod or Apple TV devices.

Data that stays local:
- Setup context and troubleshooting notes in `~/homepod/`.

This skill does NOT:
- Send undeclared network requests.
- Execute mutating control commands without target confirmation.
- Modify files outside `~/homepod/` for storage.
- Modify its own `SKILL.md`.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `smart-home` - Cross-vendor smart-home architecture and reliability patterns
- `siri` - Siri interaction and intent quality troubleshooting
- `wifi` - Local network diagnostics for latency and packet-loss issues
- `audio` - Audio routing, quality, and playback reliability workflows
- `ios` - iOS-side Home app and device configuration support

## Feedback

- If useful: `clawhub star homepod`
- Stay updated: `clawhub sync`
