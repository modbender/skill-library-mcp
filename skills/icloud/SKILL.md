---
name: iCloud
slug: icloud
version: 1.0.0
homepage: https://clawic.com/skills/icloud
description: Let agents operate your iCloud Drive, Photos, and Find My safely with local 2FA authentication and explicit confirmation gates.
changelog: Initial release with secure iCloud account integration, read-first workflows, and confirmation gates for risky actions.
metadata: {"clawdbot":{"emoji":"☁️","requires":{"bins":["python3"]},"install":[{"id":"pyicloud","kind":"pip","package":"pyicloud==2.4.1","label":"Install pyicloud 2.4.1 (pip)"}],"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for secure integration guidelines.

## When to Use

Use this skill when the user wants agents to interact with their own iCloud account: list devices, retrieve Find My status, inspect iCloud Drive, or pull photo metadata/files.
Use it for operational automation with strict safety gates, not for bypassing Apple account security.

## Architecture

Memory lives in `~/icloud/`. See `memory-template.md` for structure and status fields.

```text
~/icloud/
|-- memory.md               # Status, integration mode, and current account scope
|-- operations-log.md       # Executed commands, result checks, and rollback notes
|-- device-map.md           # Known device aliases and stable IDs
|-- drive-map.md            # iCloud Drive folder map and verified paths
`-- safety-events.md        # Confirmed risky actions and explicit approvals
```

## Quick Reference

Load only the file needed for the current task.

| Topic | File |
|-------|------|
| Setup flow | `setup.md` |
| Memory template | `memory-template.md` |
| Authentication and session handling | `auth-session.md` |
| Find My operations | `findmy-ops.md` |
| iCloud Drive operations | `drive-ops.md` |
| Photos operations | `photos-ops.md` |
| Safety boundaries and confirmations | `safety-boundaries.md` |

## Core Rules

### 1. Authenticate Locally, Never Through Chat
- Never ask the user to paste Apple password, 2FA code, session token, or app password in conversation.
- Use interactive local auth with terminal prompts or secure local input prompts only.

### 2. Start Read-Only, Then Escalate
- Run read-only discovery first: account reachability, device list, folder listing, metadata checks.
- Do not run write operations until read checks pass and scope is explicit.

### 3. Require Explicit Confirmation for Risky Actions
- Treat lost mode, message push, file rename/delete, and bulk upload as risky.
- Before running risky actions, summarize target, effect, and rollback option, then request explicit confirmation.

### 4. Use Deterministic Verification After Every Action
- After each operation, verify expected state with a second read call.
- Never report success from command exit code alone.

### 5. Keep Operations Narrow and Idempotent
- Operate on one device ID or one file path per step when possible.
- Prefer repeat-safe commands and avoid broad wildcard operations.

### 6. Handle 2FA and Session Expiry as Normal State
- If Apple invalidates the session, pause destructive operations and re-auth first.
- Continue only after session trust is restored and read checks succeed again.

### 7. Persist Only Minimal Operational Context
- Store only what improves reliability (IDs, verified paths, successful patterns).
- Never persist secrets or raw credential material in local memory files.

## Common Traps

- Asking for Apple credentials in chat -> immediate privacy and trust failure.
- Running write operations before discovery -> wrong device/path targeted.
- Using device names without IDs -> ambiguous actions on similarly named devices.
- Assuming session validity across days -> sudden auth failures mid-workflow.
- Executing bulk file changes without snapshot -> difficult rollback after mistakes.
- Claiming action success without re-read verification -> silent failures reach users.

## External Endpoints

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| https://idmsa.apple.com | Apple account auth payload during login | Apple ID authentication |
| https://setup.icloud.com | Session and webservice negotiation | iCloud service bootstrap |
| https://www.icloud.com | Service API requests (Drive/Photos/Find My) | iCloud operations |
| https://idmsa.apple.com.cn | Apple account auth payload (China mainland accounts) | Regional Apple ID authentication |
| https://setup.icloud.com.cn | Session and webservice negotiation (China mainland accounts) | Regional iCloud bootstrap |
| https://pypi.org | Package metadata (install time only) | Install `pyicloud` |
| https://files.pythonhosted.org | Package download (install time only) | Install `pyicloud` |

No other data is sent externally by this skill's documented workflow.

## Security & Privacy

Data that leaves your machine:
- Apple account authentication and iCloud API requests needed for requested operations.
- Package install traffic only when installing dependencies.

Data that stays local:
- Optional operational notes under `~/icloud/`.
- Local keyring entries managed by the `pyicloud` tool if the user chooses to store password.

This skill does NOT:
- Bypass Apple security flows or 2FA requirements.
- Request undeclared credentials in chat.
- Execute undeclared network endpoints.
- Modify its own SKILL file.

## Trust

By using this skill, you trust Apple iCloud endpoints and the `pyicloud` package.
Only install and run this workflow if you trust these services with your account operations.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `cloud-storage` - Cross-provider storage workflows and transfer safety checks
- `ios` - Apple device settings, permissions, and account behavior troubleshooting
- `macos` - macOS security, keychain, and runtime diagnostics for Apple tooling
- `photos` - Media management strategies when iCloud Photos is the main workload

## Feedback

- If useful: `clawhub star icloud`
- Stay updated: `clawhub sync`
