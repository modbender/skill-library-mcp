---
name: sandboxer
version: 1.0.0
description: Dispatch coding tasks to tmux sessions via Sandboxer. Use when you need to spawn Claude Code, Gemini, OpenCode, bash, or lazygit sessions in workspace repos, monitor their progress, or send them commands.
---

# Sandboxer — Dispatch Tasks to Tmux Sessions

> **Power-user skill.** Sandboxer gives agents full access to tmux sessions, workspace files, and terminal output on your server. Intended for dedicated AI machines where agents run with root access. Not for shared or untrusted environments.

Sandboxer runs on `localhost:8081`. No auth needed from localhost.

## Quick: Dispatch a Task

```bash
# 1. Spawn a Claude session in a repo
curl "localhost:8081/api/create?type=claude&dir=/root/workspaces/AGENT/data/repos/PROJECT"

# 2. Send it a task
curl "localhost:8081/api/send?session=SESSION_NAME&text=Fix+the+failing+tests"

# 3. Check progress
curl "localhost:8081/api/session-monitor?session=SESSION_NAME"

# 4. Kill when done
curl "localhost:8081/api/kill?session=SESSION_NAME"
```

Session types: `claude`, `bash`, `lazygit`, `gemini`, `opencode`

## Workspace Structure

Sandboxer manages `/root/workspaces/` — a single git repo containing all agent workspaces.

```
/root/workspaces/                          ← git repo (Sandboxer commits this)
├── .gitignore                             ← tracks only .md, .gitignore, cronjobs/
├── <agent-name>/                          ← one folder per OpenClaw agent
│   ├── AGENTS.md                          ← agent behavior rules
│   ├── SOUL.md, USER.md, TOOLS.md         ← agent identity & config
│   ├── MEMORY.md                          ← curated long-term memory
│   ├── TODO.md                            ← workspace task list (P1/P2/P3)
│   ├── CLAUDE.md                          ← coding rules for this workspace
│   ├── memory/YYYY-MM-DD.md               ← daily memory logs
│   ├── cronjobs/                          ← cron configs (tracked by git)
│   └── data/
│       └── repos/                         ← software projects (git clones)
│           ├── <project-a>/               ← separate git repo
│           │   ├── CLAUDE.md              ← project-specific coding rules
│           │   └── ...source code...
│           └── <project-b>/
```

### Key rules:
- **`data/repos/` contains separate git repos** — each project has its own `.git`, branches, remotes
- **The workspace `.gitignore` excludes `data/`** — repo contents stay in their own git, not the workspace commit
- **The workspace git only tracks**: `.md` files, `.gitignore`, and `cronjobs/`
- **Always read CLAUDE.md / AGENTS.md** in both workspace AND repo before dispatching work to a session

## API Reference

| Endpoint | What |
|----------|------|
| `GET /api/sessions` | List all sessions (status: running/idle/done/error) |
| `GET /api/create?type=T&dir=D` | Spawn session |
| `GET /api/session-monitor?session=S` | Last 20 lines + status + duration |
| `GET /api/capture?session=S` | Full terminal output |
| `GET /api/send?session=S&text=T` | Send keystrokes |
| `GET /api/forward?session=S&task=T` | Ctrl+C then send task |
| `GET /api/kill?session=S` | Kill session |
| `GET /api/workspaces` | List workspaces (with repos) |
| `GET /api/workspace-repos?workspace=W` | List repos in workspace |
| `GET /api/repo-tree?path=P` | Repo file tree with git status |
| `GET/POST /api/workspace/W/file/PATH` | Read/write workspace files |
| `POST /api/auto-commit?workspace=W` | Commit workspace changes |

`POST /api/create` accepts JSON body with `notify_url` — gets called when session finishes.
