# Squad Control Setup Guide

## Prerequisites
- An OpenClaw instance (VPS, local machine, Windows/WSL, etc.)
- A Squad Control account at https://squadcontrol.ai

---

## Step 1 — Get your API Key

1. Sign in to Squad Control
2. Go to **Settings → OpenClaw Integration**
3. Click **Generate API Key** — copy it now (shown once)
4. Note your workspace slug (shown in the connect snippet)

---

## Step 2 — Add env vars to OpenClaw

Edit `~/.openclaw/openclaw.json` and add:

```json
{
  "env": {
    "SC_API_URL": "https://squadcontrol.ai",
    "SC_API_KEY": "mc_your_api_key_here"
  }
}
```

Then restart: `openclaw gateway restart`

**About SC_API_KEY scopes:**
- **Workspace-scoped key** — bound to a single workspace. `/api/tasks/pending` returns only that workspace's tasks. Good for single-workspace setups.
- **Account-scoped key** — spans all workspaces in your account. `/api/tasks/pending` returns tasks from all workspaces, each with an embedded `workspace` object containing repo URL, GitHub token, and concurrency settings. **Recommended for multi-workspace setups** — no local workspace config needed.

> Both key types are fully supported. If you're only using one workspace, a workspace-scoped key works fine. If you're managing multiple projects from one OpenClaw instance, generate an account-scoped key in Squad Control → Settings → API Keys.

---

## Step 3 — Set up the polling cron job

> **Security note:** `SC_API_URL` and `SC_API_KEY` are already set as env vars in Step 2.
> The cron message below does **not** embed them — OpenClaw injects them from your config automatically.
> Never paste your API key directly into a cron message; it would be stored in plaintext in `~/.openclaw/cron/jobs.json`.

Run this command once in your terminal:

```bash
openclaw cron add \
  --name "squad-control-poll" \
  --every 15m \
  --session isolated \
  --message "Use the squad-control skill to check for and execute pending tasks."
```

Verify it's scheduled:
```bash
openclaw cron list
```

Test immediately (should return HEARTBEAT_OK if no pending tasks):
```bash
openclaw cron run <jobId>
```

---

## Step 4 — (Optional) Set up GitHub access for private repos

If your workspace repository is private:

1. Go to **Settings → Project Repository → GitHub Personal Access Token**
2. Generate a fine-grained PAT at https://github.com/settings/tokens with:
   - **Contents**: Read and write
   - **Pull requests**: Read and write
   - **Metadata**: Read-only (required)
3. Paste it and click **Save Token**

Agents will automatically receive this token when they pick up tasks and use it to clone and push to your private repo.

---

## Step 5 — Create agents and tasks

1. Go to **Agents → Create Agent** (e.g. a Developer agent)
2. Go to **Tasks → New Task**, assign it to your agent
3. Wait up to 15 min (or click Run on the cron job to test immediately)
4. Watch the agent pick it up and work

---

## Architecture

```
Squad Control (cloud)             OpenClaw (your machine)
  ├── Task kanban              ←→   ├── Polls /api/tasks/pending every 15m
  ├── Agent definitions             ├── Parses workspace.repoUrl + githubToken
  ├── Thread history                ├── Clones repo, does work
  └── Review flow                   ├── Creates PRs, posts results to thread
                                    └── Reports success or failure back
```

Pull-based: OpenClaw polls Squad Control. No public URL or port forwarding needed.
