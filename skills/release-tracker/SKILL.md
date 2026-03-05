---
name: release-tracker
description: >
  Track GitHub repository releases and generate prioritized summaries.
  Supports multiple repos, custom priority keywords, and delivery to
  Discord (forum posts or channel messages), Telegram, Slack, or plain text.
  Use when setting up automated release monitoring, checking for new versions
  of any GitHub repo, or generating changelog summaries. Triggers on track
  releases, monitor repo, check for updates, new version, release notes,
  changelog summary, setting up cron jobs for release monitoring, or any
  request to watch GitHub repos for new releases.
---

# Release Tracker

Monitor one or more GitHub repositories for new releases, generate prioritized summaries, and deliver them to configured channels.

## Prerequisites

- `gh` CLI installed and authenticated (`gh auth status`)
- For Discord delivery: Discord channel configured in OpenClaw

## Quick Start

### Single Repo Setup

Set up tracking for one repo with a cron job:

```
1. Create a config file at <workspace>/release-tracker.json (see Configuration)
2. Create a cron job (isolated, daily) that runs the check
3. The cron reads config, checks GitHub, compares versions, posts if new
```

### Multi-Repo Setup

Add multiple repos to the `repos` array in config. Each repo has independent version tracking and priority rules.

## Configuration

Store config at `<workspace>/release-tracker.json`:

```json
{
  "repos": [
    {
      "owner": "openclaw",
      "repo": "openclaw",
      "displayName": "OpenClaw",
      "priorities": ["discord", "voice", "telegram", "cron", "agent"],
      "outputChannel": "<your-discord-channel-id>",
      "outputFormat": "discord-forum",
      "language": "en",
      "includePrerelease": false
    }
  ],
  "versionStore": "release-tracker-state.json",
  "schedule": "0 10 * * *",
  "timezone": "UTC"
}
```

### Config Fields

- `repos[].owner` / `repos[].repo` — GitHub owner/repo
- `repos[].displayName` — friendly name for output header
- `repos[].priorities` — keywords to sort higher in summary (matched against changelog text)
- `repos[].outputChannel` — Discord channel/forum ID for delivery
- `repos[].outputFormat` — `discord-forum` | `discord-channel` | `telegram` | `slack` | `text`
  - `discord-forum`: create a new forum post per release
  - `discord-channel`: send a message to a Discord channel
  - `telegram`: send a message to a Telegram chat/channel/group
  - `slack`: send a message to a Slack channel
  - `text`: return plain text (for piping to other tools)
- `repos[].language` — `zh` | `en` (summary language)
- `repos[].includePrerelease` — track pre-release/RC versions
- `repos[].filter` — optional, `stable` | `all` (default: `stable`)
- `versionStore` — filename for tracking last-seen versions (relative to workspace)
- `schedule` — cron expression for check frequency
- `timezone` — timezone for cron schedule

## Workflow

### Check for New Releases

1. Read config from `release-tracker.json`
2. Read version state from `<versionStore>`
3. For each repo:
   ```bash
   gh release list --repo <owner>/<repo> --limit 5 --json tagName,publishedAt,isPrerelease
   ```
4. Compare latest tag against stored version
5. If new version found, proceed to summarize

### Generate Summary

1. Fetch release content:
   ```bash
   gh release view <tag> --repo <owner>/<repo> --json body
   ```
2. If release body is sparse, also check local CHANGELOG if the package is installed:
   ```bash
   cat /opt/homebrew/lib/node_modules/<package>/CHANGELOG.md
   ```
3. Parse and categorize changes into sections:
   - **Priority items** — lines matching any `priorities` keywords, shown first
   - **Features** — new capabilities
   - **Breaking changes** — marked with ⚠️
   - **Fixes** — bug fixes relevant to user (skip internal/CI fixes)
   - **Security** — collapsed at bottom unless critical
   - Skip: CI/test-only changes, dependency bumps, internal refactors

### Prioritization Rules

Sort entries within each section:
1. Lines matching `priorities` keywords → top
2. User-facing changes → middle
3. Internal/infrastructure → bottom
4. Omit: trivial fixes, test-only changes, doc typos

### Format Output

#### Discord Forum (`discord-forum`)

```
Title: 📦 v{version}

Body:
## {displayName} v{version}

### ⭐ Key Features
{priority matches + features, formatted as bold headers with descriptions}

### ⚠️ Breaking Changes
{breaking changes with migration notes}

### 🔧 Fixes
{relevant fixes, grouped by area}

### 🛡️ Security
{security fixes, brief}
```

#### Discord Channel (`discord-channel`)

Compact single-message format, max 2000 chars.

#### Telegram (`telegram`)

Same structure as Discord Channel but respects Telegram formatting (markdown v2). Max 4096 chars.

#### Slack (`slack`)

Same structure, uses Slack mrkdwn formatting. Max 3000 chars.

#### Text (`text`)

Plain markdown, no emoji headers.

### Deliver

Based on `outputFormat`:
- `discord-forum`: `message(action=thread-create, channelId=<outputChannel>, threadName=<title>, message=<body>)`
- `discord-channel`: `message(action=send, channel=discord, target=<outputChannel>, message=<body>)`
- `telegram`: `message(action=send, channel=telegram, target=<outputChannel>, message=<body>)`
- `slack`: `message(action=send, channel=slack, target=<outputChannel>, message=<body>)`
- `text`: return as tool result

### Update State

After successful delivery, update version store:
```json
{
  "openclaw/openclaw": {
    "lastVersion": "2026.2.22-2",
    "lastCheckedAt": "2026-02-24T10:00:00+09:00",
    "lastPublishedAt": "2026-02-22T..."
  }
}
```

## Cron Setup

Create the cron job for automated checking:

```
Name: release-tracker
Schedule: {config.schedule} with tz {config.timezone}
Session: isolated
Payload: agentTurn with message referencing this skill
Delivery: none (skill handles its own delivery)
```

The cron message should instruct the agent to:
1. Read `release-tracker.json` for config
2. Read `release-tracker-state.json` for last versions
3. Check each repo via `gh release list`
4. If new releases found, generate summaries and deliver
5. Update state file

## Manual Check

User can trigger manually: "check for new releases" or "any updates on openclaw?"

The agent should:
1. Load config
2. Run the check workflow
3. Report findings conversationally (not necessarily in forum format)
