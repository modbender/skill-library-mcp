# 👷 Claude Code Supervisor

**Autonomous supervision for Claude Code sessions. The missing link between "junior developer" and "dark factory."**

---

## The Problem

You kick off a Claude Code session to fix a bug. It's humming along — then hits an API 500 error mid-stream. It stops. You're asleep, or sailing, or just doing something else. Hours later you check back: dead session, no progress.

Or it finishes the fix, tests pass, code is committed — but nobody noticed. It's sitting there at a prompt, done, waiting for a human who isn't watching.

This is the gap between **Level 3** (you're the code reviewer) and **Level 5** (the dark factory) in [Dan Shapiro's five levels of AI-assisted programming](https://www.danshapiro.com/blog/2026/01/the-five-levels-from-spicy-autocomplete-to-the-software-factory/). At Level 3-4, the AI does the work, but a human is still babysitting the process — nudging past errors, approving permissions, noticing when it's done. At Level 5, the lights are off. The robots don't need you watching.

**Claude Code Supervisor is the night shift foreman.** It watches your coding agents so you don't have to. When something goes wrong, it triages the problem with a fast LLM call. If it's a transient API error, it nudges. If it's stuck, it escalates. If it's done, it tells you. If everything's fine, it shuts up.

## How It Works

```
Claude Code (running in tmux)
  │
  │  Stop / Error / Notification
  ▼
┌─────────────────────────────┐
│  Bash pre-filter (μs)       │  ← Skip obvious non-issues
│  "Is this even worth        │     (mid-conversation turns,
│   thinking about?"          │      rate limits, auth events)
└──────────┬──────────────────┘
           │ ambiguous cases only
           ▼
┌─────────────────────────────┐
│  Fast LLM triage (~1s)      │  ← Haiku / local LLM classifies:
│  "Is this session stuck,    │     FINE → log silently
│   done, or needs help?"     │     NEEDS_NUDGE → notify
└──────────┬──────────────────┘     STUCK → notify
           │ actionable only        DONE → notify
           ▼                        ESCALATE → notify
┌─────────────────────────────┐
│  Your agent harness         │  ← OpenClaw, webhook, ntfy,
│  decides what to do         │     Slack, custom script, etc.
└─────────────────────────────┘
```

Most events never leave the bash layer. The ones that do get assessed by a cheap, fast model — not your expensive primary context. You only get pinged when it matters.

## Quick Start

```bash
# Clone
git clone https://codeberg.org/johba/claude-code-supervisor.git
cd claude-code-supervisor

# Install into your project
./scripts/install-hooks.sh ~/my-project

# Edit the config it created
vim ~/my-project/.claude-code-supervisor.yml

# Launch Claude Code in tmux as usual — hooks fire automatically
```

## Configuration

The skill creates `.claude-code-supervisor.yml` in your project:

```yaml
triage:
  # What does the thinking. Anything that reads stdin and writes stdout.
  command: "claude -p --no-session-persistence"   # Uses Claude Code's own auth
  model: "claude-haiku-4-20250414"                # Fast and cheap

  # Or use a local model:
  # command: "ollama run llama3.2"

notify:
  # Where to send alerts. Gets a JSON string as last argument.
  command: "openclaw gateway call wake --params"

  # Or use anything:
  # command: "curl -s -X POST https://ntfy.sh/my-topic -d"
  # command: "/path/to/my-slack-notify.sh"
```

**No hard dependencies on any agent harness.** OpenClaw is one option. Webhooks, ntfy, Slack, a custom script — whatever receives the notification can decide what to do next.

## The Decision Flow (Option D)

Not every event needs an LLM call. Bash handles the obvious stuff:

| Event | Bash says... | LLM triage? |
|-------|-------------|-------------|
| `Stop` — agent mid-conversation | "It's working, leave it alone" | ❌ |
| `Stop` — shell prompt returned | "Might be done or stuck" | ✅ |
| `Stop` — hit max tokens | "Context limit, needs attention" | ✅ |
| `Error` — 429 rate limit | "Transient, will resolve" | ❌ |
| `Error` — 500 API error | "Agent probably stuck on this" | ✅ |
| `Notification` — auth event | "Internal, ignore" | ❌ |
| `Notification` — permission prompt | "Needs a decision" | ✅ |
| `Notification` — idle | "Waiting for human input" | ✅ |

The LLM classifies ambiguous cases as: `FINE`, `NEEDS_NUDGE`, `STUCK`, `DONE`, or `ESCALATE`. Only actionable verdicts trigger notifications.

## What's in the Box

```
claude-code-supervisor/
├── SKILL.md                          # AgentSkill spec (for OpenClaw / ClawHub)
├── supervisor.yml.example            # Config template
├── scripts/
│   ├── install-hooks.sh              # One-command project setup
│   ├── lib.sh                        # Config loading, notify, triage wrappers
│   ├── triage.sh                     # LLM assessment dispatcher
│   ├── watchdog.sh                   # Dead session detector (pure bash, no LLM)
│   └── hooks/
│       ├── on-stop.sh                # Stop event → bash pre-filter → triage
│       ├── on-error.sh               # Tool failure → bash pre-filter → triage
│       └── on-notify.sh              # Notification → bash pre-filter → triage
├── references/
│   ├── state-patterns.md             # Terminal pattern matching guide
│   └── escalation-rules.md           # When to nudge vs escalate vs wait
└── assets/
    └── supervisor-state.template.json
```

## The Watchdog (Who Watches the Watchman?)

Hooks depend on Claude Code being alive. If the process hits account limits, gets OOM-killed, or the machine reboots — no hooks fire. Silence.

`watchdog.sh` is a pure bash script (no LLM, no Claude Code dependency) that runs on a timer and checks: *is the tmux session still there? Is Claude Code still running inside it?* If something is dead and nobody reported it, it notifies.

```bash
# System cron — every 15 minutes
*/15 * * * * /path/to/claude-code-supervisor/scripts/watchdog.sh
```

It's deliberately dumb. No LLM, no complex logic, no dependencies that could also be down. When the triage model is unreachable because your account limit hit, the watchdog still works. Belts and suspenders.

## Toward the Dark Factory

The [dark factory](https://simonwillison.net/2026/Jan/28/the-five-levels/) metaphor is about AI systems that run without human oversight — where "nobody reviews AI-produced code, ever." We're not there yet, and maybe we shouldn't be. But the path from Level 3 to Level 5 isn't one giant leap. It's a series of small automations that chip away at the "human watching a terminal" bottleneck.

This skill is one of those automations. It doesn't replace judgment — it just makes sure judgment gets applied when it matters, not wasted on staring at a screen waiting for something to happen.

The lights aren't off yet. But you can go to sleep.

## Status

Early/experimental. Built for [OpenClaw](https://github.com/openclaw/openclaw) but designed to work with any agent harness. Contributions welcome.

## License

MIT
