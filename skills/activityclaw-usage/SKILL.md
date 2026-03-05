# ActivityClaw Plugin Usage

## When to Use

Use this skill when the user asks about:
- Recent agent activities or actions
- What the agent has been doing
- Tool usage tracking or monitoring
- File operations history (reads, writes, edits)
- Command execution history
- Web searches or fetches performed
- Message sending activity
- Sub-agent spawning

## Prerequisites

The ActivityClaw plugin must be installed:
```bash
npm install -g @rmruss2022/activityclaw
openclaw plugins install @rmruss2022/activityclaw
```

## Quick Start

Check if ActivityClaw is installed and running:
```bash
openclaw activityclaw status
```

## Commands

### View Dashboard
Open the visual activity dashboard in browser:
```bash
openclaw activityclaw dashboard
```
This opens http://localhost:18796 with real-time activity feed.

### Check Status
Show current status and configuration:
```bash
openclaw activityclaw status
```

### Start/Stop
Manually control the service:
```bash
openclaw activityclaw start
openclaw activityclaw stop
```

### Configuration
Reconfigure port or database location:
```bash
openclaw activityclaw setup
```

## What ActivityClaw Tracks

- **📝 File Operations** - Creates, edits, reads
- **⚡ Commands** - Shell executions via exec
- **🔍 Web Activity** - Searches and fetches
- **💬 Messages** - Outbound messages to channels
- **🚀 Sub-agents** - Spawned agent sessions

## Dashboard Features

The dashboard at http://localhost:18796 provides:
- **Real-time activity feed** - Live stream of all agent actions
- **Activity filters** - View by type (files, commands, web, messages)
- **Statistics** - Total activities, last hour count, active agents
- **Auto-refresh** - Updates every 5 seconds

## Example Usage

**User asks:** "What files have I been working on today?"

**Response:**
```bash
openclaw activityclaw dashboard
```
Then check the "📝 Create" and "✏️ Edit" filters in the dashboard to see recent file operations.

**User asks:** "Show me recent command executions"

**Response:**
```bash
openclaw activityclaw dashboard
```
Filter by "⚡ Exec" to see command history.

**User asks:** "What has the agent been doing?"

**Response:**
```bash
openclaw activityclaw status
```
This shows a summary, then suggest opening the dashboard for details:
```bash
openclaw activityclaw dashboard
```

## Troubleshooting

If activities aren't showing:
1. Check plugin status: `openclaw plugins list`
2. Verify service is running: `openclaw activityclaw status`
3. Start if stopped: `openclaw activityclaw start`
4. Check dashboard URL: http://localhost:18796

If port is in use:
```bash
openclaw activityclaw setup
# Choose a different port
```

## Technical Details

- **Port:** 18796 (default, configurable)
- **Database:** SQLite at `~/.openclaw/activity-tracker/activities.db`
- **Tracking:** Real-time via `tool_result_persist` hook
- **Storage:** All data stays local

## Repository

GitHub: https://github.com/rmruss2022/ActivityClaw
npm: @rmruss2022/activityclaw
