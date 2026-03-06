# Privacy Policy — Productivity Skill v2.7

## Overview

This skill is a **local-only, instruction-based** AI productivity coach. It does **not** contain any executable code, install scripts, or network communication logic. All data is stored locally on your device and is never uploaded, transmitted, or shared with any external service.

## Consent Model

Before creating any files, the skill's `FIRST_TIME_SETUP` protocol will:

1. Explain what data will be stored and where
2. Ask for your **explicit consent** before proceeding
3. If you decline, the skill operates in **stateless mode** (no files created, session-only coaching)

## Data Storage

All data is stored in a `memory` folder at `/home/ubuntu/productivity-skill/memory/`. Here is a complete breakdown:

| File | Data Stored | Purpose | Created When | Deletion |
| :--- | :--- | :--- | :--- | :--- |
| `profile.md` | User preferences (list mode, reminder times) | Personalize skill behavior | After consent | Delete file to reset |
| `goals.md` | Your 5 core annual goals and 8 life areas | Align tasks with priorities | After goal-setting | Delete file to clear |
| `inbox.md` | Raw, unprocessed thoughts and ideas | Quick capture | When you say "record:" | Delete lines or file |
| `calendar.md` | Calendar events with dates and times | Remember commitments | When you add events | Delete lines or file |
| `lists/*.md` | Flexible task lists by context | Manage actionable tasks | When you add tasks | Delete files or lines |
| `custom_rules.md` | Personalized rules from your feedback | Adapt AI to your workflow | After your explicit approval | Delete file to reset |
| `task_history.md` | Log of completed and postponed tasks | Insights during reviews | When tasks complete | Delete file to clear |

## What This Skill Does NOT Do

- **No ambient monitoring**: Energy sensing is based only on your explicit text (word choices, emotional vocabulary) and file content (item counts in inbox/lists). It does **not** monitor typing speed, typing rhythm, response timing, mouse movements, keystroke patterns, or any other behavioral signals.
- **No external data transmission**: No data is ever sent to any server, API, or third party.
- **No silent rule creation**: Custom rules are always shown to you and require your explicit approval before being saved.
- **No credential storage**: This skill does not store any passwords, API keys, or authentication tokens. Google Calendar integration (if used) relies on the platform's OAuth flow, which is user-initiated and managed by the platform.
- **No code execution**: This skill is instruction-only. It contains no scripts, binaries, or executable payloads.

## Tool Usage

This skill declares the following tool permissions:

| Tool | Purpose | Consent |
| :--- | :--- | :--- |
| `schedule` | Set reminders for calendar events and reviews | Asked before each use |
| `file_read` | Read memory files for context | Covered by initial consent |
| `file_write` | Write to memory files for persistence | Covered by initial consent |
| `google-calendar` (MCP, optional) | Sync events to Google Calendar | Only when you explicitly request it; requires your OAuth authentication |

## How to Delete Your Data

You can delete the entire `/home/ubuntu/productivity-skill/memory/` folder at any time to permanently erase all personal data associated with this skill. The skill will then trigger the first-time setup protocol (with consent request) if you use it again.

## Contact

For questions about this privacy policy, please open an issue on the [GitHub repository](https://github.com/yewubin-jpg/productivity-skill).
