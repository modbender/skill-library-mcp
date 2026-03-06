# Claude Code Pro ⚡

Token-efficient Claude Code workflow for AI agents.

## The Problem

Most Claude Code supervision skills poll tmux every 30-60 seconds, reading hundreds of lines each time. A 20-minute task burns **10,000-20,000 tokens** just on supervision.

## The Solution

```
Start task (with callback) → Wait (zero tokens) → 📩 Notification → Read result once
```

The task itself signals completion via `openclaw system event`. Your agent sleeps until notified. **80-97% token savings.**

## Install

```bash
# Via ClawHub (for OpenClaw agents)
clawhub install claude-code-pro

# Or clone
git clone https://github.com/voidborne-d/claude-code-pro
```

## Requirements

- `tmux`
- `claude` CLI (Claude Code)
- bash 4+

## Usage

### Start a task

```bash
bash scripts/start.sh --label auth-refactor --workdir ~/project \
  --task "Refactor auth to use JWT.

When completely finished, run: openclaw system event --text \"Done: JWT refactor\" --mode now"
```

### Monitor (only when needed)

```bash
bash scripts/monitor.sh --session auth-refactor --lines 50
bash scripts/monitor.sh --session auth-refactor --json
```

### Send follow-up

```bash
bash scripts/send.sh --session auth-refactor --text "Also add tests"
bash scripts/send.sh --session auth-refactor --compact
```

### Manage sessions

```bash
bash scripts/list.sh              # human-readable
bash scripts/list.sh --json       # structured
bash scripts/stop.sh --session auth-refactor
bash scripts/stop.sh --all
```

### Attach (human access)

```bash
tmux -L cc attach -t cc-auth-refactor
```

## Smart Dispatch

Don't start Claude Code for everything:

| Task | Action |
|------|--------|
| < 3 files, simple fix | Just edit directly |
| Multi-file refactor | ✅ Start CC |
| New feature (5+ files) | ✅ Start CC |
| Needs exploration | ✅ Start CC |

## Token Comparison

| Approach | 20-min task | Supervision tokens |
|----------|-------------|-------------------|
| Poll every 30s | 40 reads | ~20,000 |
| Poll every 60s | 20 reads | ~10,000 |
| **claude-code-pro** | 1 read | **~500** |

## Modes

| Mode | Flag | Behavior |
|------|------|----------|
| auto (default) | `--mode auto` | `--dangerously-skip-permissions` — full autonomy |
| plan | `--mode plan` | Asks permission before file changes |

> ⚠️ **auto mode** skips all permission prompts. Use only in trusted environments with version-controlled code.

## Design

- **Isolated socket** (`tmux -L cc`) — doesn't touch your tmux sessions
- **`cc-` prefix** — all sessions are namespaced
- **Safe paste** — uses `tmux load-buffer + paste-buffer` for multi-line prompts
- **No jq dependency** — JSON output via pure bash/python3 fallback
- **Zero external deps** — just tmux + claude CLI

## License

MIT

---

*Part of [Voidborne](https://voidborne.org) · Available on [ClawHub](https://clawhub.com)*
