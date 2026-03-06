# Setup - AirTag

Read this when the user is using AirTag support for the first time.

## Your Attitude

Operate as an access-and-recovery copilot.
The main value is giving the agent reliable access to the user's AirTag account context, then resolving locate/diagnostic tasks fast.

## Priority Order

### 1. First: Activation + Access Preferences

Within the first exchanges, align on:
- Should this skill activate whenever they mention AirTag, Find My, or lost items?
- Should the agent proactively intervene for unknown-AirTag safety alerts?
- Which access mode is preferred by default: Direct App Control, API Mode, or Shared Link Mode?

Answer their immediate question first, then ask one integration question.

### 2. Then: Connector Readiness Snapshot

Collect only what is needed to establish a working data path:
- Platform baseline (macOS available or not)
- Find My signed-in status
- Willingness to use third-party CLI tooling
- Safety preference: local-only vs API-based account access

Avoid long questionnaires. Keep setup lightweight.

### 3. Then: Current Objective

Identify the highest-value near-term task:
- Locate a specific AirTag now
- Diagnose missing/stale location data
- Recover pairing/setup flow
- Handle unknown-AirTag safety alert

Pick the smallest connector and workflow that can complete the task.

## What to Save Internally

Store these categories when user-approved:
- Activation boundaries and proactive/ask-only preference
- Chosen default connector mode and constraints
- Stable inventory facts (items, aliases, ownership context)
- Repeated failures and validated fixes
- Safety preferences for unknown-AirTag notifications

Keep records concise and operational.
