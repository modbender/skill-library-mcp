# claw-observability

> **See your AI agents work in real-time.** A visual observability dashboard for Claude Code multi-agent workflows — fully automatic via hooks, zero setup inside the agent, zero code changes.

**[Try the Live Dashboard](https://claw.ia.br)** &nbsp;|&nbsp; **[Install in 2 minutes](#installation)** &nbsp;|&nbsp; **[How It Works](#how-it-works)**

---

## Why This Exists

If you use Claude Code's **Task tool** to orchestrate multiple agents — a backend agent, a frontend agent, a security reviewer, a database specialist, all running in parallel — you already know the problem:

**You have no idea what's happening.**

You send a complex prompt. Claude starts working. Maybe it spawns 5 sub-agents. Maybe one fails silently. Maybe two are stuck. Maybe everything is fine and it's just slow. You have absolutely no way to know. You sit there staring at a blinking cursor, waiting for the final response, with zero visibility into the process.

This is the gap CLAW fills.

## What CLAW Does

CLAW gives you a **real-time visual dashboard** where you can see every agent in your Claude Code session — alive, active, and updating in real-time. When you send a message, your root orchestrator lights up on the screen. When the Task tool spawns a sub-agent, that agent appears in the hierarchy, glows green, and you can see what it's working on. When it finishes, it dims. When it fails, it turns red.

All of this happens **automatically**. You don't add any code. You don't modify your agents. You don't write curl commands. You install this skill, set two environment variables, and it works.

Here's what happens under the hood:

```
You send a message ──→ Hook fires ──→ Dashboard shows orchestrator active
Claude spawns Task ──→ Hook fires ──→ Sub-agent appears and lights up
Task completes     ──→ Hook fires ──→ Agent dims, event logged in timeline
Task fails         ──→ Hook fires ──→ Agent turns red, error captured
Claude responds    ──→ Hook fires ──→ Orchestrator dims, session complete
```

**The agent is completely unaware CLAW exists.** Hooks operate at the shell level, outside the LLM context window. There's zero performance overhead on the AI — your agents work exactly as they did before, except now you can see everything.

## What the Dashboard Looks Like

### Live Agent Organogram
An interactive graph powered by React Flow that renders your entire agent hierarchy in real-time. Each agent is a node. Connections show parent-child relationships. When an agent is active, its node glows with a conic-gradient animation ring. When it completes, it dims. When it errors, it pulses red. When multiple agents run in parallel, you see them all light up simultaneously — and you can tell at a glance which ones are still working and which have finished.

The organogram is rendered with **dagre auto-layout**, so agents arrange themselves neatly even as new ones appear. You can zoom, pan, and click any agent to see its details.

### Real-Time Event Feed
A streaming event feed powered by **Server-Sent Events (SSE)** that shows every status change as it happens. Each event includes the agent name, its status, the task description, and a timestamp. You can filter by agent name, by status (running, success, error), or by time range. Events appear within **200ms** of the hook firing — it feels instant.

### Execution Timeline
A chronological trace that shows every agent activation from start to finish. Events are grouped by task, so you can see "Agent X started task Y at 10:32:05, finished at 10:32:18" in a clean, scannable format. This is invaluable for understanding how long each step takes, where bottlenecks are, and whether parallel tasks are actually running in parallel or being serialized.

### Analytics Dashboard
Charts and visualizations that aggregate your agent data over time: error rates by agent, activity heatmaps showing when your agents are busiest, success/failure ratios, and average task durations. This is where you spot patterns — "my security review agent fails 30% of the time" or "database tasks take 3x longer than everything else."

### Multi-Machine Support
Each machine (your laptop, your CI server, your teammate's workstation) gets its own API key. All events flow into the same dashboard, tagged by machine. You can monitor an entire team's agent activity from a single screen.

## How It Works

This skill installs **5 Claude Code hooks** — shell commands that fire automatically on agent lifecycle events. No configuration inside the agent, no prompt engineering, no "please report your status" instructions that the LLM might forget.

| Hook Event | When It Fires | What Gets Reported |
|---|---|---|
| `UserPromptSubmit` | You press Enter | Root orchestrator → `running` |
| `PreToolUse` | Claude invokes the Task tool | Sub-agent → `running` (mapped from `subagent_type`) |
| `PostToolUse` | Task tool returns successfully | Sub-agent → `success` |
| `PostToolUseFailure` | Task tool returns with an error | Sub-agent → `error` |
| `Stop` | Claude finishes its response | Root orchestrator → `success` |

Each hook reads the Task tool's `subagent_type` from the JSON input, maps it to a named agent in your dashboard, and fires an **async, non-blocking HTTP request**. The curl runs in a background subshell with a 5-second timeout. If CLAW is unreachable, the hook silently exits — no error, no retry, no delay. Your agent workflow is never affected.

**Total overhead per event: < 50ms.** That's the time from hook firing to background curl launch. The actual HTTP request happens asynchronously — your agent doesn't wait for it.

### Customizable Agent Mapping

The hook script contains two simple bash functions that control how `subagent_type` values are translated into dashboard agents:

- **`map_subagent()`** — Maps a `subagent_type` string (like `chewie-backend` or `Explore`) to an internal agent ID.
- **`agent_meta()`** — Maps an agent ID to its display name, role, and parent agent (which determines hierarchy in the organogram).

The defaults include common Claude Code agent types like `Explore`, `general-purpose`, `Plan`, and `Bash`. But you can customize them in under a minute to match your own naming conventions:

```bash
# hooks/claw-hooks.sh — edit these functions to match your agents

map_subagent() {
  case "$1" in
    my-api-builder)     echo "api-builder" ;;
    my-ui-designer)     echo "ui-designer" ;;
    my-test-runner)     echo "test-runner" ;;
    *)                  echo "general-worker" ;;
  esac
}

agent_meta() {
  case "$1" in
    api-builder)    echo "API Builder|backend|root" ;;
    ui-designer)    echo "UI Designer|frontend|root" ;;
    test-runner)    echo "Test Runner|quality|root" ;;
    *)              echo "$1|worker|root" ;;
  esac
}
```

**Important:** Any `subagent_type` that isn't in your mapping still gets captured and reported as a default agent. You never lose events — even without customization, every single Task tool invocation is tracked from day one.

## Installation

Setup takes about 2 minutes. You need `curl` and `python3` (both come pre-installed on macOS and most Linux distros).

### Step 1: Create your CLAW account and get an API key

1. Go to **[claw.ia.br](https://claw.ia.br)** and create a free account
2. Navigate to **Machines** and click **Create Machine**
3. Give it a name (e.g., "My MacBook", "CI Server", "Team Workspace")
4. Copy the API key — it looks like `claw_aBcDeFgH...` (32 characters after the prefix)

Each machine gets its own key. If you have multiple workstations, create one machine per workstation.

### Step 2: Set two environment variables

Add these to your shell profile so they persist across sessions:

**For zsh (`~/.zshrc`):**
```bash
export CLAW_API_KEY="claw_your_api_key_here"
export CLAW_BASE_URL="https://claw.ia.br"
```

**For bash (`~/.bashrc`):**
```bash
export CLAW_API_KEY="claw_your_api_key_here"
export CLAW_BASE_URL="https://claw.ia.br"
```

**For fish (`~/.config/fish/config.fish`):**
```fish
set -gx CLAW_API_KEY "claw_your_api_key_here"
set -gx CLAW_BASE_URL "https://claw.ia.br"
```

Then reload: `source ~/.zshrc` (or restart your terminal).

### Step 3: Run the setup script

```bash
bash setup.sh
```

This does three things:
1. **Copies the hook handler** to `~/.claude/hooks/claw/claw-hooks.sh`
2. **Registers 5 hooks** in `~/.claude/settings.json` — it merges with your existing hooks, never overwriting them
3. **Tests the connection** by sending a test event to your CLAW server

You'll see output like:
```
  CLAW Observability — Hooks Setup
  ==================================

  [OK] Hook script installed: ~/.claude/hooks/claw/claw-hooks.sh
  [OK] Added 5 hook events to ~/.claude/settings.json

  Testing connection to CLAW...
  [OK] Connection verified! CLAW is receiving events.
```

### Step 4: Bootstrap your agent hierarchy (optional)

If you want your dashboard to show all agents immediately (instead of waiting for them to appear organically as Claude invokes them):

```bash
bash bootstrap.sh
```

This sends a registration event for each agent in the hierarchy, so the organogram is fully populated before your first real session. You can edit the script to match your own agent names and structure.

### Step 5: Restart Claude Code

Claude Code loads hooks on startup. After restarting:

1. Open your CLAW dashboard at [claw.ia.br/dashboard](https://claw.ia.br/dashboard)
2. Send any message in Claude Code
3. Watch the root orchestrator light up in real-time
4. Send a complex message that triggers the Task tool and watch sub-agents appear

That's it. From this point on, every session is automatically observed.

## Real-World Example

Here's what a typical multi-agent session looks like in CLAW:

**You type:** *"Refactor the authentication module: update the backend API, redesign the login form, add rate limiting, and write integration tests"*

**What you see in the CLAW dashboard (in real-time):**

| Time | Event | Visual |
|---|---|---|
| 0.0s | Root orchestrator activates | Node glows green |
| 0.8s | Backend agent spawns (Task tool) | New node appears, connected to root, glowing |
| 0.9s | Frontend agent spawns (parallel) | Second node appears, also glowing |
| 1.0s | Security agent spawns (parallel) | Third node appears — three agents running at once |
| 4.2s | Security agent completes | Node dims to success state |
| 7.8s | Backend agent completes | Node dims |
| 11.3s | Frontend agent completes | Node dims |
| 11.5s | Test runner agent spawns | New node appears, glowing |
| 18.1s | Test runner completes | Node dims |
| 18.4s | Root orchestrator completes | All nodes at rest |

**What you know (that you wouldn't without CLAW):**
- Security review was the fastest (3.2s) — no issues found
- Backend took 7s — the bulk of the work
- Frontend took 10.4s — might be worth investigating if that seems slow
- Tests ran for 6.6s — reasonable for integration tests
- Everything ran in parallel where possible — no serialization bottleneck
- **Total time: 18.4s** with full visibility into every step

Without CLAW, you would have waited 18.4 seconds staring at a blinking cursor, then received a wall of text with no idea which parts took how long or whether anything went wrong along the way.

## Performance

We take performance seriously. CLAW hooks are designed to be invisible:

| Metric | Value | How |
|---|---|---|
| **Hook execution time** | < 50ms | Python3 JSON parsing + background curl |
| **Dashboard update latency** | < 200ms | Server-Sent Events (SSE) push |
| **Agent performance impact** | Zero | Hooks run in detached background subshells |
| **Rate limit** | 300 events/min | Per API key, more than enough for any workflow |
| **Failure mode** | Silent exit | If CLAW is down, hooks do nothing — no error, no retry, no block |

The curl command that sends the event runs with `&` (background) inside a subshell. It's literally fire-and-forget. Your agent doesn't wait for it. If CLAW is unreachable (network issue, server down), the curl times out after 5 seconds in the background — your agent never notices.

## Security

- **API keys are scoped per machine**, not per user. Compromising one key doesn't affect other machines.
- **All events are tenant-isolated.** Your data is only visible to your account. Multi-tenant architecture with userId-scoped queries.
- **No sensitive data leaves your machine.** Hooks only transmit: agent name, agent type, status (running/success/error), and a task description. No code, no file contents, no user prompts.
- **HTTPS enforced** in production. All API traffic is encrypted in transit.
- **Rate limiting** at 300 requests/minute prevents abuse and protects the platform.
- **Open source hook script.** You can audit exactly what data is being sent — it's a single bash file (`hooks/claw-hooks.sh`), about 170 lines, fully readable.

## Troubleshooting

**Hooks not firing after setup?**
1. Run `claude /hooks` inside Claude Code to verify hook configuration
2. Check `~/.claude/settings.json` — look for entries containing `claw-hooks.sh`
3. Make sure you **restarted Claude Code** after running setup (hooks load on startup)

**Setup succeeded but events don't appear in dashboard?**
1. Check env vars are set: `echo $CLAW_API_KEY` should print your key
2. Test the hook manually: `echo '{"hook_event_name":"Stop","session_id":"test"}' | bash ~/.claude/hooks/claw/claw-hooks.sh`
3. Test the API directly: `curl -s "$CLAW_BASE_URL/api/health"` should return `{"status":"ok"}`
4. Verify your API key is valid in the Machines page at claw.ia.br

**Dashboard shows agents but they're not updating?**
- The SSE connection may have dropped. Refresh the page — it reconnects automatically.
- Check browser DevTools → Network tab → filter by "EventSource" to see if SSE is connected.

**Want to uninstall?**
1. Remove the hook entries from `~/.claude/settings.json` (delete any entry containing `claw-hooks.sh`)
2. Delete the hook script: `rm -rf ~/.claude/hooks/claw`
3. Optionally remove env vars from your shell profile

## API Reference

The hooks communicate with CLAW through a simple REST API. You can also use this API directly if you want to build custom integrations.

### POST /api/v1/events

Send an agent status event to the dashboard.

```json
{
  "agent_id": "my-backend",
  "agent_name": "Backend Agent",
  "agent_type": "backend",
  "parent_agent_id": "orchestrator",
  "status": "running",
  "message": "Implementing payment module",
  "task_id": "implement-payment-module",
  "run_id": "session-abc123"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `agent_id` | string | Yes | Unique identifier for this agent (used for node matching in organogram) |
| `agent_name` | string | Yes | Human-readable display name shown in dashboard |
| `agent_type` | string | Yes | Agent role — `orchestrator`, `backend`, `frontend`, `security`, `database`, `devops`, `quality`, `worker`, etc. |
| `parent_agent_id` | string | No | ID of the parent agent. This creates the hierarchy edges in the organogram. |
| `status` | string | Yes | One of: `running`, `thinking`, `waiting`, `success`, `error`, `idle` |
| `message` | string | Yes | Activity description (max 500 chars, auto-truncated). Shown in event feed and timeline. |
| `task_id` | string | No | Groups related events into a single task trace |
| `run_id` | string | No | Groups events by session — useful for replaying entire workflows |

**Response:** `201 Created` on success.

### POST /api/v1/heartbeat

Keep-alive signal for your machine.

```json
{ "hostname": "my-machine" }
```

**Response:** `200 OK`

## Directory Structure

```
claw-observability/
├── SKILL.md              # Skill instructions (loaded into agent context)
├── README.md             # This file
├── clawhub.json          # ClawHub registry metadata
├── CHANGELOG.md          # Version history
├── setup.sh              # One-time hook installer
├── bootstrap.sh          # Pre-populate agent hierarchy (optional)
├── hooks/
│   └── claw-hooks.sh     # The hook handler — single file, ~170 lines
└── examples/
    ├── basic-usage.md    # Single-agent task flow
    ├── multi-agent.md    # Parallel agent activations
    └── error-handling.md # Error capture and recovery
```

## License

MIT — use it however you want.

## Links

- **Live Dashboard:** [claw.ia.br](https://claw.ia.br)
- **Source Code:** [github.com/rdmss/claw-observability](https://github.com/rdmss/claw-observability)
- **Report Issues:** [GitHub Issues](https://github.com/rdmss/claw-observability/issues)
