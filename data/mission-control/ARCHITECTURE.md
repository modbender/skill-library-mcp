# Mission Control Architecture

## How Dashboard and MoltBot Communicate

Mission Control uses an **asymmetric bidirectional architecture** with GitHub as the central hub:

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│    Dashboard    │         │     GitHub      │         │     MoltBot     │
│   (Browser)     │         │   (Hub + Host)  │         │   (Local AI)    │
└────────┬────────┘         └────────┬────────┘         └────────┬────────┘
         │                           │                           │
         │  1. User moves task       │                           │
         │     to "In Progress"      │                           │
         │ ────────────────────────► │                           │
         │   (GitHub API commit)     │                           │
         │                           │                           │
         │                           │  2. GitHub Webhook        │
         │                           │     notifies MoltBot      │
         │                           │ ────────────────────────► │
         │                           │   (HTTPS via Tailscale)   │
         │                           │                           │
         │                           │                           │  3. MoltBot
         │                           │                           │     works on task
         │                           │                           │
         │                           │  4. MoltBot pushes        │
         │                           │     updates via Git       │
         │                           │ ◄──────────────────────── │
         │                           │   (git commit + push)     │
         │                           │                           │
         │  5. Dashboard auto-       │                           │
         │     refreshes from GitHub │                           │
         │ ◄──────────────────────── │                           │
         │   (GitHub API fetch)      │                           │
         │                           │                           │
```

## Communication Channels

### Channel 1: Dashboard → MoltBot (GitHub Webhook)

**Trigger:** Any push to the repository (including task changes)

**Flow:**
1. Dashboard saves change to GitHub via API (`data/tasks.json`)
2. GitHub detects push event
3. GitHub sends webhook directly to MoltBot's endpoint

**Transport:** HTTPS via Tailscale Funnel

**Setup:**
1. Go to repo Settings → Webhooks → Add webhook
2. Payload URL: `https://your-machine.tail1234.ts.net/hooks/github?token=YOUR_TOKEN`
3. Content type: `application/json`
4. Events: "Just the push event"

**Payload:** Standard GitHub push event containing:
- Commit information
- Changed files list
- Repository metadata

MoltBot processes the webhook and checks if `data/tasks.json` was modified to determine if action is needed.

### Channel 2: MoltBot → Dashboard (Git)

**Trigger:** MoltBot completes work, updates subtasks, or adds comments

**Flow:**
1. MoltBot modifies `data/tasks.json` (via CLI or direct edit)
2. MoltBot commits and pushes to GitHub
3. GitHub Pages automatically redeploys
4. Dashboard fetches latest data on next refresh/poll

**Transport:** Git over HTTPS (standard `git push`)

**CLI Example:**
```bash
# Mark subtask as done
mc-update.sh done task_001 sub_001

# Add progress comment
mc-update.sh comment task_001 "Color variables defined. Working on toggle."

# Complete task (moves to Review)
mc-update.sh complete task_001 "Dark mode implemented with system preference detection"

# Push all changes
mc-update.sh push "Complete dark mode implementation"
```

## Why This Architecture?

### Direct Webhook (Dashboard → MoltBot)

Using GitHub's native webhook system provides:

- **Speed** — No intermediate Action runner (saves 5-15 seconds)
- **Simplicity** — Fewer moving parts, less maintenance
- **Cost** — No GitHub Actions minutes consumed
- **Reliability** — GitHub's webhook infrastructure is battle-tested

### Git as Sync Layer (MoltBot → Dashboard)

Using Git for MoltBot's updates provides:

- **Built-in history** — Every change is a commit with timestamp and message
- **Conflict resolution** — Git handles concurrent edits
- **Offline resilience** — Changes queue locally until push succeeds
- **Auditability** — Complete log of who changed what and when

### GitHub as Hub

GitHub serves three roles:

1. **Data store** — `tasks.json` is the source of truth
2. **Webhook sender** — Notifies MoltBot on every push
3. **Static hosting** — GitHub Pages serves the dashboard

## Tailscale Setup

Tailscale creates a secure private network, allowing GitHub webhooks to reach your local MoltBot.

### Install Tailscale

```bash
# macOS
brew install tailscale
sudo tailscaled install-system-daemon
tailscale up

# Linux
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

### Enable Funnel

Funnel exposes your MoltBot to the internet securely:

```bash
# Enable HTTPS funnel for MoltBot gateway port
tailscale funnel 18789
```

### Get Your Funnel URL

```bash
tailscale funnel status
# Output: https://your-machine.tail1234.ts.net:443 -> http://127.0.0.1:18789
```

Use this URL (with your webhook path) as the GitHub webhook Payload URL.

## Security Considerations

### Webhook Authentication

The webhook URL includes a token parameter:
```
https://your-machine.tail1234.ts.net/hooks/github?token=YOUR_SECRET_TOKEN
```

Generate a secure token:
```bash
openssl rand -hex 32
```

### Network Security

**Tailscale Funnel:**
- Traffic encrypted end-to-end
- No ports exposed on local network
- Authenticated via Tailscale identity

### GitHub Token Scope

The dashboard uses a Personal Access Token with `repo` scope:
- Can read/write repository contents
- Cannot access other repositories (unless explicitly granted)
- Stored only in browser localStorage

## Latency Characteristics

| Path | Typical Latency |
|------|-----------------|
| Dashboard → GitHub | 200-500ms |
| GitHub → MoltBot webhook | 1-3 seconds |
| MoltBot → GitHub push | 1-3 seconds |
| GitHub Pages deploy | 30-90 seconds |
| **Total round-trip** | **~1-2 minutes** |

## Summary

Mission Control uses a **hub-and-spoke model** with GitHub at the center:

- **Direct webhook** notifies MoltBot of changes (fast, simple)
- **Git push** syncs MoltBot's progress back to the dashboard
- **No GitHub Actions** required for the notification flow
- **Tailscale Funnel** provides secure access without port forwarding

This architecture is simple, fast, and leverages existing infrastructure without complex server setups.
