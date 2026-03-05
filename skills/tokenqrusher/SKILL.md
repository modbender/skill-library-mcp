---
name: tokenQrusher
description: Token optimization system for OpenClaw reducing costs 50-80%
version: 2.1.1
author: qsmtco
license: MIT
homepage: https://github.com/qsmtco/tokenQrusher
metadata:
  openclaw:
    requires:
      bins:
        - python3
        - node
    emoji: "💰"
---

# tokenQrusher Skill

## Overview

tokenQrusher reduces OpenClaw API costs by 50-80% through:
1. **Context Filtering** – Loads only necessary workspace files (up to 99% reduction for simple messages)
2. **Heartbeat Optimization** – Reduces heartbeat API calls by 75%

This is the simplified, production-ready core. Non-functional advisory components have been removed.

---

## Components

### 1. Context Hook (`token-context`)

**Event:** `agent:bootstrap`

Filters which workspace files are loaded based on message complexity.

**Config:** `~/.openclaw/hooks/token-context/config.json`

```json
{
  "enabled": true,
  "logLevel": "info",
  "dryRun": false,
  "files": {
    "simple": ["SOUL.md", "IDENTITY.md"],
    "standard": ["SOUL.md", "IDENTITY.md", "USER.md"],
    "complex": ["SOUL.md", "IDENTITY.md", "USER.md", "TOOLS.md", "AGENTS.md", "MEMORY.md", "HEARTBEAT.md"]
  }
}
```

**How it works:**
- Extracts the user's latest message
- Classifies complexity (simple/standard/complex)
- Keeps only allowed files, discards the rest
- Sets `context.bootstrapFiles` to the filtered list

**Savings:**
- Simple greetings → 2 files (99% token reduction)
- Standard tasks → 3 files (90%+ reduction)
- Complex tasks → all files (full context)

**Rationale:** Simple messages don’t need documentation, memory logs, or tool references. Only identity and personality are required.

### 2. Heartbeat Optimizer (`token-heartbeat`)

**Event:** `agent:bootstrap` (for heartbeat polls)

Optimizes heartbeat check schedule to dramatically reduce API calls.

**Config:** `~/.openclaw/hooks/token-heartbeat/config.json`

```json
{
  "enabled": true,
  "intervals": {
    "email": 7200,
    "calendar": 14400,
    "weather": 14400,
    "monitoring": 7200
  },
  "quietHours": { "start": 23, "end": 8 }
}
```

**How it works:**
- Determines if enough time has elapsed since last check
- Skips checks that are not due
- Honors quiet hours (23:00–08:00 by default)
- Returns `HEARTBEAT_OK` when nothing needs checking

**Optimization Table:**

| Check | Default Interval | Optimized | Reduction |
|-------|------------------|-----------|-----------|
| Email | 60 min | 120 min | 50% |
| Calendar | 60 min | 240 min | 75% |
| Weather | 60 min | 240 min | 75% |
| Monitoring | 30 min | 120 min | 75% |

**Result:** 48 checks/day → 12 checks/day (**75% fewer API calls**)

### 3. Shared Module (`token-shared`)

Pure functions used by both hooks:
- `classifyComplexity(message)` → complexity level
- `getAllowedFiles(level, config)` → file list
- `isValidFileName(name)` → path traversal protection
- `loadConfigCached(logFn)` → 60s TTL config caching
- Maybe/Either patterns (no exceptions for control flow)

---

## External Endpoints

This skill does **not** call any external network endpoints. All operations are local to your machine.

---

## Security & Privacy

- **100% local execution** – No data leaves your system.
- **No external telemetry** – No calls to third‑party servers.
- **Configuration** read only from local hook configs.
- **File validation** prevents path traversal attacks.
- **No environment secrets** required.

---

## Model Invocation Note

Hooks run automatically:

- `token-context` runs on every `agent:bootstrap` (every user message).
- `token-heartbeat` runs on heartbeat polls.
No manual intervention needed after enabling the hooks.

---

## Trust Statement

By installing this skill, you trust that the code operates locally and does not transmit your workspace data. Review the open‑source implementation on GitHub before installing.

---

## CLI Commands

After installation, the `tokenqrusher` command is available.

### `tokenqrusher context <prompt>`

Recommends which context files should be loaded for a given prompt.

```bash
$ tokenqrusher context "hi"
Complexity: simple (confidence: 95%)
Files: SOUL.md, IDENTITY.md
Savings: 71%
```

### `tokenqrusher status [--verbose]`

Shows system status.

```bash
$ tokenqrusher status
=== tokenQrusher Status ===

Hooks:
  ✓ token-context   (Filters context)
  ✓ token-heartbeat (Optimizes heartbeat)
```

### `tokenqrusher install [--hooks] [--all]`

Installs/enables hooks.

```bash
$ tokenqrusher install --hooks
✓ Enabled: token-context
✓ Enabled: token-heartbeat
```

---

## Configuration

All hook configs are JSON files stored in:
`~/.openclaw/hooks/<hook-name>/config.json`

You can edit these to customize behavior (e.g., adjust file lists, intervals, or quiet hours). Changes are reloaded after 60 seconds (config cache TTL).

---

## Design Principles

- **Deterministic** – Same input → same output.
- **Pure functions** – No hidden side effects.
- **Immutability** – Frozen data structures.
- **No exceptions for control flow** – Uses Result/Either types.
- **Thread‑safe** – RLock protected shared state.
- **Exhaustive typing** – Full type hints.

---

## Performance

| Operation | Latency | Memory |
|-----------|---------|--------|
| Context classification | <1 ms | <1 MB |
| Heartbeat check | <0.5 ms | <0.5 MB |

Negligible overhead per agent message.

---

## Troubleshooting

### Hook not loading?

```bash
# Check status
openclaw hooks list

# Should show "✓ ready" next to token-context and token-heartbeat

# Enable if missing
openclaw hooks enable token-context
openclaw hooks enable token-heartbeat

# Restart gateway
openclaw gateway restart
```

### Changes not taking effect?

Config cache TTL is 60 seconds. Restart the gateway for immediate effect.

---

## Migration from v2.0.x

v2.1.0 removes non‑functional components. If upgrading:

1. Disable and remove old hooks:
   ```bash
   openclaw hooks disable token-model
   openclaw hooks disable token-usage
   openclaw hooks disable token-cron
   rm -rf ~/.openclaw/hooks/token-model
   rm -rf ~/.openclaw/hooks/token-usage
   rm -rf ~/.openclaw/hooks/token-cron
   ```

2. Update the skill:
   ```bash
   clawhub update tokenQrusher
   ```

3. Re‑install remaining hooks:
   ```bash
   tokenqrusher install --hooks
   ```

4. Restart gateway:
   ```bash
   openclaw gateway restart
   ```

**Removed commands:** `tokenqrusher model`, `budget`, `usage`, `optimize`. They no longer exist.

---

## License

MIT. See `LICENSE` file in repository.

---

## Credits

- **Design & Implementation:** Lieutenant Qrusher (qsmtco)
- **Review:** Captain JAQ (SMTCo)
- **Framework:** OpenClaw Team

Built with OpenClaw: https://github.com/openclaw/openclaw
