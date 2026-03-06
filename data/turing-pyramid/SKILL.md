---
name: turing-pyramid
description: 10-need psychological hierarchy for AI agents. Run on heartbeat → get prioritized actions.
metadata:
  clawdbot:
    emoji: "🔺"
    requires:
      env:
        - WORKSPACE
      bins:
        - bash
        - jq
        - bc
        - grep
        - find
    primaryEnv: WORKSPACE
---

# Turing Pyramid

10-need psychological hierarchy for AI agents. Run on heartbeat → get prioritized actions.

**Customization:** Tune decay rates, weights, patterns. Defaults are starting points. See `TUNING.md`.

**Ask your human before:** Changing importance values, adding/removing needs, enabling external actions.

---

## Requirements

**System binaries (must be in PATH):**
```
bash, jq, grep, find, date, wc, bc
```

**Environment (REQUIRED — no fallback):**
```bash
# Scripts will ERROR if WORKSPACE is not set
export WORKSPACE="/path/to/your/workspace"
```
⚠️ **No silent fallback.** If WORKSPACE is unset, scripts exit with error.
This prevents accidental scanning of unintended directories.

**Post-install (ClawHub):**
```bash
# ClawHub doesn't preserve executable bits — fix after install:
chmod +x ~/.openclaw/workspace/skills/turing-pyramid/scripts/*.sh
chmod +x ~/.openclaw/workspace/skills/turing-pyramid/tests/**/*.sh
```
Why: Unix executable permissions (+x) are not preserved in ClawHub packages.
Scripts work fine with `bash scripts/run-cycle.sh`, but `./scripts/run-cycle.sh` needs +x.

---

## Data Access & Transparency

**What this skill reads (via grep/find scans):**
- `MEMORY.md`, `memory/*.md` — for connection/expression/understanding signals
- `SOUL.md`, `SELF.md` — for integrity/coherence checks
- `research/`, `scratchpad/` — for competence/understanding activity
- Dashboard files, logs — for various need assessments

**What this skill writes:**
- `assets/needs-state.json` — current satisfaction/deprivation state
- `assets/audit.log` — append-only log of all mark-satisfied calls (v1.12.0+)

**Privacy considerations:**
- Scans use grep patterns, not semantic analysis — they see keywords, not meaning
- State file contains no user content, only need metrics
- Audit log records reasons given for satisfaction claims
- No data is transmitted externally by the skill itself

**Limitations & Trust Model:**
- `mark-satisfied.sh` trusts caller-provided reasons — audit log records claims, not verified facts
- Some actions in `needs-config.json` reference external services (Moltbook, web search) — marked with `"external": true, "requires_approval": true`
- External actions are **suggestions only** — the skill doesn't execute them, the agent decides
- If you don't want external action suggestions, set their weights to 0

**Network & System Access:**
- Scripts contain **no network calls** (no curl, wget, ssh, etc.) — verified by grep scan
- Scripts contain **no system commands** (no sudo, systemctl, docker, etc.)
- All operations are local: grep, find, jq, bc, date on WORKSPACE files only
- The skill **suggests** actions (including some that mention external services) but **never executes** them

**Required Environment Variables:**
- `WORKSPACE` — path to agent workspace (REQUIRED, no fallback)
- `TURING_CALLER` — optional, for audit trail (values: "heartbeat", "manual")

**Audit trail (v1.12.0+):**
All `mark-satisfied.sh` calls are logged with:
- Timestamp, need, impact, old→new satisfaction
- Reason (what action was taken) — **scrubbed for sensitive patterns**
- Caller (heartbeat/manual)

**Sensitive data scrubbing (v1.12.3+):**
Before writing to audit log, reasons are scrubbed:
- Long tokens (20+ chars) → `[REDACTED]`
- Credit card patterns → `[CARD]`
- Email addresses → `[EMAIL]`
- password/secret/token/key values → `[REDACTED]`
- Bearer tokens → `Bearer [REDACTED]`

View audit: `cat assets/audit.log | jq`

---

## Quick Start

```bash
./scripts/init.sh                        # First time
./scripts/run-cycle.sh                   # Every heartbeat  
./scripts/mark-satisfied.sh <need> [impact]  # After action
```

---

## The 10 Needs

```
┌───────────────┬─────┬───────┬─────────────────────────────────┐
│ Need          │ Imp │ Decay │ Meaning                         │
├───────────────┼─────┼───────┼─────────────────────────────────┤
│ security      │  10 │ 168h  │ System stability, no threats    │
│ integrity     │   9 │  72h  │ Alignment with SOUL.md          │
│ coherence     │   8 │  24h  │ Memory consistency              │
│ closure       │   7 │  12h  │ Open threads resolved           │
│ autonomy      │   6 │  24h  │ Self-directed action            │
│ connection    │   5 │   6h  │ Social interaction              │
│ competence    │   4 │  48h  │ Skill use, effectiveness        │
│ understanding │   3 │  12h  │ Learning, curiosity             │
│ recognition   │   2 │  72h  │ Feedback received               │
│ expression    │   1 │   8h  │ Creative output                 │
└───────────────┴─────┴───────┴─────────────────────────────────┘
```

---

## Core Logic

**Satisfaction:** 0.0–3.0 (floor=0.5 prevents paralysis)  
**Tension:** `importance × (3 - satisfaction)`

### Action Probability (v1.13.0)

6-level granular system:

```
┌─────────────┬────────┬──────────────────────┐
│ Sat         │ Base P │ Note                 │
├─────────────┼────────┼──────────────────────┤
│ 0.5 crisis  │  100%  │ Always act           │
│ 1.0 severe  │   90%  │ Almost always        │
│ 1.5 depriv  │   75%  │ Usually act          │
│ 2.0 slight  │   50%  │ Coin flip            │
│ 2.5 ok      │   25%  │ Occasionally         │
│ 3.0 perfect │    0%  │ Skip (no action)     │
└─────────────┴────────┴──────────────────────┘
```

**Tension bonus:** `bonus = (tension × 50) / max_tension`

### Impact Selection (v1.13.0)

6-level granular matrix with smooth transitions:

```
┌─────────────┬───────┬────────┬───────┐
│ Sat         │ Small │ Medium │ Big   │
├─────────────┼───────┼────────┼───────┤
│ 0.5 crisis  │   0%  │    0%  │ 100%  │
│ 1.0 severe  │  10%  │   20%  │  70%  │
│ 1.5 depriv  │  20%  │   35%  │  45%  │
│ 2.0 slight  │  30%  │   45%  │  25%  │
│ 2.5 ok      │  45%  │   40%  │  15%  │
│ 3.0 perfect │  —    │    —   │  —    │ (skip)
└─────────────┴───────┴────────┴───────┘
```

- **Crisis (0.5)**: All-in on big actions — every need guaranteed ≥3 big actions
- **Perfect (3.0)**: Skip action selection — no waste on satisfied needs

**ACTION** = do it, then `mark-satisfied.sh`  
**NOTICED** = logged, deferred

---

## Protection Mechanisms

```
┌─────────────┬───────┬────────────────────────────────────────┐
│ Mechanism   │ Value │ Purpose                                │
├─────────────┼───────┼────────────────────────────────────────┤
│ Floor       │  0.5  │ Minimum sat — prevents collapse        │
│ Ceiling     │  3.0  │ Maximum sat — prevents runaway         │
│ Cooldown    │   4h  │ Deprivation cascades once per 4h       │
│ Threshold   │  1.0  │ Deprivation only when sat ≤ 1.0        │
└─────────────┴───────┴────────────────────────────────────────┘
```

**Day/Night Mode (v1.11.0):** Decay slows at night to reduce pressure during rest hours.
- Configure in `assets/decay-config.json`
- Default: 06:01-22:00 = day (×1.0), 22:01-06:00 = night (×0.5)
- Disable with `"day_night_mode": false`

**Base Needs Isolation:** Security (10) and Integrity (9) are protected:
- They influence lower needs (security → autonomy)
- Lower needs cannot drag them down
- Only `integrity → security (+0.15)` and `autonomy → integrity (+0.20)` exist

---

## Cross-Need Impact

**on_action:** Completing A boosts connected needs  
**on_deprivation:** A staying low (sat ≤ 1.0) drags others down

```
┌─────────────────────────┬──────────┬─────────────┬───────────────────────┐
│ Source → Target         │ on_action│ on_deprived │ Why                   │
├─────────────────────────┼──────────┼─────────────┼───────────────────────┤
│ expression → recognition│   +0.25  │      -0.10  │ Express → noticed     │
│ connection → expression │   +0.20  │      -0.15  │ Social sparks ideas   │
│ connection → understand │   -0.05  │         —   │ Socratic effect       │
│ competence → recognition│   +0.30  │      -0.20  │ Good work → respect   │
│ autonomy → integrity    │   +0.20  │      -0.25  │ Act on values         │
│ closure → coherence     │   +0.20  │      -0.15  │ Threads → order       │
│ security → autonomy     │   +0.10  │      -0.20  │ Safety enables risk   │
└─────────────────────────┴──────────┴─────────────┴───────────────────────┘
```

### Tips

- **Leverage cascades:** Connection easy? Do it first — boosts expression (+0.20)
- **Watch spirals:** expression ↔ recognition can create mutual deprivation
- **Autonomy is hub:** Receives from 5 sources. Keep healthy.
- **Socratic effect:** connection → understanding: -0.05. Dialogue exposes ignorance. Healthy!

Full matrix: `assets/cross-need-impact.json`

---

## Example Cycle

```
🔺 Turing Pyramid — Cycle at Tue Feb 25 05:36
======================================

⚠️ Deprivation cascades:
   autonomy (sat=0.5) → integrity: -0.25 (now: 1.75)
   autonomy (sat=0.5) → expression: -0.20 (now: 0.80)

Current tensions:
  closure: tension=21 (sat=0, dep=3)
  connection: tension=15 (sat=0, dep=3)

📋 Decisions:

▶ ACTION: closure (tension=21, sat=0.00)
  → coherence: +0.20, competence: +0.15, autonomy: +0.10

▶ ACTION: connection (tension=15, sat=0.00)
  → expression: +0.20, recognition: +0.15
  → understanding: -0.05 (Socratic effect)
```

---

## Integration

Add to `HEARTBEAT.md`:
```bash
/path/to/skills/turing-pyramid/scripts/run-cycle.sh
```

---

## Customization

### You Can Tune (no human needed)

**Decay rates** — `assets/needs-config.json`:
```json
"connection": { "decay_rate_hours": 4 }
```
Lower = decays faster. Higher = persists longer.

**Action weights** — same file:
```json
{ "name": "reply to mentions", "impact": 2, "weight": 40 }
```
Higher weight = more likely selected. Set 0 to disable.

**Scan patterns** — `scripts/scan_*.sh`:
Add your language patterns, file paths, workspace structure.

### Ask Your Human First

- **Adding needs** — The 10-need hierarchy is intentional. Discuss first.
- **Removing needs** — Don't disable security/integrity without agreement.

---

## File Structure

```
turing-pyramid/
├── SKILL.md                    # This file
├── CHANGELOG.md                # Version history
├── assets/
│   ├── needs-config.json       # ★ Main config (tune this!)
│   ├── cross-need-impact.json  # ★ Cross-need matrix
│   └── needs-state.json        # Runtime state (auto)
├── scripts/
│   ├── run-cycle.sh            # Main loop
│   ├── mark-satisfied.sh       # State + cascades
│   ├── apply-deprivation.sh    # Deprivation cascade
│   └── scan_*.sh               # Event detectors (10)
└── references/
    ├── TUNING.md               # Detailed tuning guide
    └── architecture.md         # Technical docs
```

---

## Security Model

**Decision framework, not executor.** Outputs suggestions — agent decides.

```
┌─────────────────────┐      ┌─────────────────────┐
│   TURING PYRAMID    │      │       AGENT         │
├─────────────────────┤      ├─────────────────────┤
│ • Reads local JSON  │      │ • Has web_search    │
│ • Calculates decay  │ ───▶ │ • Has API keys      │
│ • Outputs: "★ do X" │      │ • Has permissions   │
│ • Zero network I/O  │      │ • DECIDES & EXECUTES│
└─────────────────────┘      └─────────────────────┘
```

### ⚠️ Security Warnings

```
┌────────────────────────────────────────────────────────────────┐
│ THIS SKILL READS WORKSPACE FILES THAT MAY CONTAIN PII         │
│ AND OUTPUTS ACTION SUGGESTIONS THAT CAPABLE AGENTS MAY        │
│ AUTO-EXECUTE USING THEIR OWN CREDENTIALS.                     │
└────────────────────────────────────────────────────────────────┘
```

**1. Sensitive file access (no tokens required):**
- Scans read: `MEMORY.md`, `memory/*.md`, `SOUL.md`, `AGENTS.md`
- Also scans: `research/`, `scratchpad/` directories
- Risk: May contain personal notes, PII, or secrets
- **Mitigation:** Edit `scripts/scan_*.sh` to exclude sensitive paths:
  ```bash
  # Example: skip private directory
  find "$MEMORY_DIR" -name "*.md" ! -path "*/private/*"
  ```

**2. Action suggestions may trigger auto-execution:**
- Config includes: "web search", "post to Moltbook", "verify vault"
- This skill outputs text only — it CANNOT execute anything
- Risk: Agent runtimes with auto-exec may act on suggestions
- **Mitigation:** In `assets/needs-config.json`, remove or disable external actions:
  ```json
  {"name": "post to Moltbook", "impact": 2, "weight": 0}
  ```
  Or configure your agent runtime to require approval for external actions.

**3. Self-reported state (no verification):**
- `mark-satisfied.sh` trusts caller input
- Risk: State can be manipulated by dishonest calls
- Impact: Only affects this agent's own psychological accuracy
- **Mitigation:** Enable action logging in `memory/` to audit completions:
  ```bash
  # run-cycle.sh already logs to memory/YYYY-MM-DD.md
  # Review logs periodically for consistency
  ```

### Script Audit (v1.14.4)

**scan_*.sh files verified — NO network or system access:**
```
┌─────────────────────────────────────────────────────────┐
│ ✗ curl, wget, ssh, nc, fetch     — NOT FOUND           │
│ ✗ /etc/, /var/, /usr/, /root/    — NOT FOUND           │
│ ✗ .env, .pem, .key, .credentials — NOT FOUND           │
├─────────────────────────────────────────────────────────┤
│ ✓ Used: grep, find, wc, date, jq — local file ops only │
│ ✓ find uses -P flag (never follows symlinks)           │
└─────────────────────────────────────────────────────────┘
```

**Symlink protection:** All `find` commands use `-P` (physical) mode — symlinks pointing outside WORKSPACE are not followed.

**Scan confinement:** Scripts only read paths under `$WORKSPACE`. Verify with:
```bash
grep -nE "\b(curl|wget|ssh)\b" scripts/scan_*.sh     # network tools
grep -rn "readlink\|realpath" scripts/               # symlink resolution
```

---

## Token Usage

```
┌──────────────┬─────────────┬────────────┐
│ Interval     │ Tokens/mo   │ Est. cost  │
├──────────────┼─────────────┼────────────┤
│ 30 min       │ 1.4M-3.6M   │ $2-6       │
│ 1 hour       │ 720k-1.8M   │ $1-3       │
│ 2 hours      │ 360k-900k   │ $0.5-1.5   │
└──────────────┴─────────────┴────────────┘
```

Stable agent with satisfied needs = fewer tokens.

---

## Testing

```bash
# Run all tests
WORKSPACE=/path/to/workspace ./tests/run-tests.sh

# Unit tests (9): decay, floor/ceiling, tension, probability, impact matrix, day/night, scrubbing
# Integration (3): full cycle, homeostasis stability, stress test
```

---

## Version

**v1.14.1** — Mid-impact actions, 6-level matrices, expanded test coverage. Full changelog: `CHANGELOG.md`
