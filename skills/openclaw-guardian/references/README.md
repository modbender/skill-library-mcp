# openclaw-guardian

> **The missing safety layer for AI agents.**

## Why This Exists

OpenClaw is powerful — it gives AI agents direct access to shell commands, file operations, email, browser automation, and more. That power is exactly what makes it useful, but it's also what makes people nervous.

The community has been vocal: *"security nightmare"*, *"what if the AI deletes my files?"*, *"I don't trust it with my credentials"*. OpenClaw's existing safety (sandbox + allowlist + manual confirmation) only covers `exec`, and it's all-or-nothing — either you trust the agent completely, or you block everything.

**openclaw-guardian** fills that gap. It sits between the AI's decision and the actual execution, automatically assessing risk and routing dangerous operations through independent Guardian Agents for voting-based approval. Think of it as a board of directors that reviews high-stakes decisions before they happen — except it takes 2 seconds, not 2 weeks.

The key insight: **95% of what an AI agent does is harmless** (reading files, fetching URLs, writing notes). Only ~5% is potentially dangerous (deleting files, running destructive commands, accessing secrets). Guardian only intervenes on that 5%, so you get safety without sacrificing speed.

## How It Works

```
AI Agent wants to run a tool (e.g., exec "rm -rf /tmp/data")
                    ↓
        ┌───────────────────────┐
        │   Risk Assessor       │  ← Keyword rules, 0ms, no model call
        │   Scores 0-100        │
        └───────────┬───────────┘
                    ↓
    ┌───────────────┼───────────────┐
    ↓               ↓               ↓
  0-30            31-70           71-100
 Fast Lane     Light Review     Full Vote
 (just go)    (1 Guardian)    (3 Guardians)
    ↓               ↓               ↓
 Execute      Single review    Parallel vote
              all angles       different angles
                    ↓               ↓
              approve/reject   majority rules
                                    ↓
                            approve → execute
                            reject → block + tell user why
```

### The Three Lanes

| Lane | Risk Score | Guardians | Latency | When |
|------|-----------|-----------|---------|------|
| Fast | 0-30 | 0 | ~0ms | Reading files, fetching URLs, normal operations |
| Light | 31-70 | 1 (comprehensive) | ~1-2s | Writing config files, sending messages |
| Full | 71-100 | 3 (specialized) | ~2-4s | `rm -rf`, `sudo`, accessing `.ssh`, `.env` |

### Guardian Perspectives

Each Guardian in Full Vote mode reviews from a **different angle** — this isn't redundant voting, it's multi-perspective analysis:

| Guardian | What It Checks |
|----------|---------------|
| **Safety** | Will this break something? Is it destructive? Can the system recover? |
| **Privacy** | Does this touch credentials, API keys, personal data, or secrets? |
| **Permission** | Is this within the scope of what the user authorized? |
| **Reversibility** | Can this be undone? What's the blast radius if it goes wrong? |
| **Comprehensive** | All of the above (used in Light Review when only 1 Guardian is needed) |

### Why Not Just Use LLMs for Everything?

Guardian's Risk Assessor uses **zero-cost keyword rules** — no model calls for scoring. Pattern matching like `rm -rf` → +40 points, `sudo` → +25 points is instant and deterministic. LLM-based Guardian evaluation is optional and only triggered for the ~5% of operations that actually need review.

## Quick Start (One Command)

### 1. Clone into your OpenClaw workspace

```bash
cd ~/.openclaw/workspace
git clone https://github.com/fatcatMaoFei/openclaw-guardian.git
```

### 2. Register the plugin

Add to your `openclaw.json`:

```json
{
  "plugins": {
    "load": {
      "paths": ["./openclaw-guardian"]
    },
    "entries": {
      "openclaw-guardian": {
        "enabled": true
      }
    }
  }
}
```

### 3. Restart

```bash
openclaw gateway restart
```

That's it. Guardian is now active. Every tool call goes through risk assessment automatically.

## Customization

### Adjust Risk Policies

Edit `default-policies.json` to match your comfort level:

```json
{
  "thresholds": {
    "low": 30,
    "high": 70
  },
  "policies": [
    {
      "tool": "exec",
      "baseScore": 50,
      "keywords": {
        "rm -rf": 40,
        "sudo ": 25,
        "kill ": 20,
        "reboot": 30,
        "shutdown": 30,
        "mkfs": 50,
        "dd if=": 40,
        "> /dev/": 50
      }
    },
    {
      "tool": "write",
      "baseScore": 15,
      "keywords": {
        ".env": 45,
        "passwd": 50,
        ".ssh": 50,
        "config.json": 30,
        "openclaw.json": 40
      }
    },
    {
      "tool": "file_delete",
      "baseScore": 40
    },
    {
      "tool": "message_send",
      "baseScore": 20
    },
    {
      "tool": "read",
      "baseScore": 5,
      "keywords": {
        ".env": 55,
        ".ssh/id_": 75,
        "passwd": 50
      }
    },
    {
      "tool": "web_fetch",
      "baseScore": 5
    }
  ]
}
```

**Want stricter security?** Lower the thresholds:
```json
{ "thresholds": { "low": 15, "high": 50 } }
```

**Want less friction?** Raise them:
```json
{ "thresholds": { "low": 50, "high": 85 } }
```

**Want to add your own dangerous keywords?** Just add them to the tool's `keywords` object with a score boost.

### Adjust Voting Rules

```json
{
  "voting": {
    "lightReview": { "guardians": 1, "threshold": 1 },
    "fullVote": { "guardians": 3, "threshold": 2 }
  }
}
```

Want 5 Guardians with 4/5 majority? Change it:
```json
{ "fullVote": { "guardians": 5, "threshold": 4 } }
```

### Trust Budget

After N consecutive approvals, Guardian auto-downgrades the review tier:

```json
{
  "trustBudget": {
    "enabled": true,
    "autoDowngradeAfter": 10
  }
}
```

Any rejection resets the counter. Disable with `"enabled": false`.

## Audit Trail

Every decision is logged to `~/.openclaw/guardian-audit.jsonl` with SHA-256 hash chaining:

```json
{
  "timestamp": "2026-02-24T09:30:00.000Z",
  "toolName": "exec",
  "riskScore": 90,
  "tier": "full",
  "votes": [
    { "guardian": "safety", "approve": false, "reason": "rm -rf on system path" },
    { "guardian": "privacy", "approve": true },
    { "guardian": "permission", "approve": false, "reason": "not explicitly authorized" }
  ],
  "approved": false,
  "hash": "a1b2c3...",
  "prevHash": "d4e5f6..."
}
```

Tamper-evident: each entry's hash includes the previous entry's hash. Break one link and the whole chain fails verification.

## Architecture

```
openclaw-guardian/
├── openclaw.plugin.json    # Plugin manifest
├── index.ts                # Entry — registers before_tool_call / after_tool_call hooks
├── src/
│   ├── risk-assessor.ts    # Keyword rule engine (0ms, no model calls)
│   ├── guardian-voter.ts   # Tiered voting with parallel execution + early termination
│   └── audit-log.ts        # SHA-256 hash-chain audit logger
├── guardians/              # Guardian system prompts (each a different review angle)
│   ├── safety.md
│   ├── privacy.md
│   ├── permission.md
│   ├── reversibility.md
│   └── comprehensive.md
└── default-policies.json   # Default risk policies (user-customizable)
```

### How It Hooks Into OpenClaw

OpenClaw's agent loop: `Model → tool_call → Tool Executor → result → Model`

Guardian registers a `before_tool_call` plugin hook. This hook fires **after** the model decides to call a tool but **before** the tool actually executes. If Guardian returns `{ block: true }`, the tool is stopped and the model receives a rejection message instead.

This is the same hook interface OpenClaw uses internally for loop detection — battle-tested, async-safe, and zero modifications to core code.

## Token Cost

| Tier | % of Operations | Extra Cost |
|------|----------------|------------|
| Fast Lane | 85-95% | 0 (rule-based only) |
| Light Review | 5-10% | ~500 tokens per review |
| Full Vote | 1-3% | ~1500 tokens per review |

**Average overhead: ~15-35% of total token usage.** Most operations cost nothing extra.

## Status

🚧 Under active development — contributions welcome.

## License

MIT
