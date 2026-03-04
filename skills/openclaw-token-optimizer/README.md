# OpenClaw Token Optimizer

**Reduce OpenClaw token usage and API costs by 50-80%**

An OpenClaw skill for smart model routing, lazy context loading, optimized heartbeats, budget tracking, and native OpenClaw 2026.2.15 features (session pruning, bootstrap size limits, cache TTL alignment).

[![ClawHub](https://img.shields.io/badge/ClawHub-openclaw--token--optimizer-blue)](https://clawhub.ai/Asif2BD/openclaw-token-optimizer)
[![Version](https://img.shields.io/badge/version-1.4.2-green)](https://github.com/Asif2BD/OpenClaw-Token-Optimizer/blob/main/CHANGELOG.md)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](https://opensource.org/licenses/Apache-2.0)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-purple)](https://openclaw.ai)

---

## 🚀 Installation

### Option 1: ClawHub (recommended)
```bash
clawhub install Asif2BD/openclaw-token-optimizer
```

Or browse to: [clawhub.ai/Asif2BD/openclaw-token-optimizer](https://clawhub.ai/Asif2BD/openclaw-token-optimizer)

### Option 2: Manual (GitHub)
```bash
git clone https://github.com/Asif2BD/OpenClaw-Token-Optimizer.git \
  ~/.openclaw/skills/openclaw-token-optimizer
```
Then add to `openclaw.json`:
```json
{
  "skills": {
    "load": {
      "extraDirs": ["~/.openclaw/skills/openclaw-token-optimizer"]
    }
  }
}
```

### One-line install prompt for your agent
> "Install the OpenClaw Token Optimizer skill from https://clawhub.ai/Asif2BD/openclaw-token-optimizer — or if ClawHub isn't available, clone https://github.com/Asif2BD/OpenClaw-Token-Optimizer and add the path to skills.load.extraDirs in openclaw.json"

---

## ✨ What's New in v1.4.x (OpenClaw 2026.2.15)

Three **native config patches** that work today with zero external dependencies:

### Session Pruning
Auto-trim old tool results when the Anthropic cache TTL expires — reduces cache re-write costs.
```json
{ "agents": { "defaults": { "contextPruning": { "mode": "cache-ttl", "ttl": "5m" } } } }
```

### Bootstrap Size Limits
Cap workspace file injection into the system prompt (20-40% reduction for large workspaces).
```json
{ "agents": { "defaults": { "bootstrapMaxChars": 10000, "bootstrapTotalMaxChars": 15000 } } }
```

### Cache Retention for Opus
Amortize cache write costs on long Opus sessions.
```json
{ "agents": { "defaults": { "models": { "anthropic/claude-opus-4-5": { "params": { "cacheRetention": "long" } } } } } }
```

### Cache TTL Heartbeat Alignment
Keep the Anthropic 1h prompt cache warm — avoid the re-write penalty.
```bash
python3 scripts/heartbeat_optimizer.py cache-ttl
# → recommended_interval: 55min (3300s)
```

---

## 🛠️ Quick Start

**1. Context optimization (biggest win):**
```bash
python3 scripts/context_optimizer.py recommend "hi, how are you?"
# → Load only 2 files, skip everything else → ~80% savings
```

**2. Model routing:**
```bash
python3 scripts/model_router.py "design a microservices architecture"
# → Complex task → Opus
python3 scripts/model_router.py "thanks!"
# → Simple ack → Sonnet (cheapest available)
```

**3. Optimized heartbeat:**
```bash
cp assets/HEARTBEAT.template.md ~/.openclaw/workspace/HEARTBEAT.md
python3 scripts/heartbeat_optimizer.py plan
```

**4. Token budget check:**
```bash
python3 scripts/token_tracker.py check
```

**5. Cache TTL alignment:**
```bash
python3 scripts/heartbeat_optimizer.py cache-ttl
# Set heartbeat to 55min to keep Anthropic 1h cache warm
```

---

## 🔍 Native OpenClaw Diagnostics (2026.2.15+)

```
/context list    → per-file token breakdown (use before applying bootstrap limits)
/context detail  → full system prompt breakdown
/usage tokens    → append token count to every reply
/usage cost      → cumulative cost summary
```

---

## 📁 Skill Structure

```
openclaw-token-optimizer/
├── SKILL.md                    ← Skill definition (loaded by OpenClaw)
├── SECURITY.md                 ← Full security audit + provenance
├── CHANGELOG.md                ← Version history
├── .clawhubsafe                ← SHA256 integrity manifest (13 files)
├── .clawhubignore              ← Files excluded from publish bundle
├── scripts/
│   ├── context_optimizer.py    ← Context lazy-loading
│   ├── model_router.py         ← Task classification + model routing
│   ├── heartbeat_optimizer.py  ← Interval management + cache-ttl alignment
│   ├── token_tracker.py        ← Budget monitoring
│   └── optimize.sh             ← Convenience CLI wrapper (calls Python scripts)
├── assets/
│   ├── config-patches.json     ← Ready-to-apply config patches
│   ├── HEARTBEAT.template.md   ← Drop-in optimized heartbeat template
│   └── cronjob-model-guide.md  ← Model selection for cron tasks
└── references/
    └── PROVIDERS.md            ← Multi-provider strategy guide
```

---

## 📊 Expected Savings

| Strategy | Context | Model | Monthly (100K tok/day) | Savings |
|---|---|---|---|---|
| Baseline (no optimization) | 50K | Sonnet | $9.00 | 0% |
| Context optimization only | 10K | Sonnet | $5.40 | 40% |
| Model routing only | 50K | Mixed | $5.40 | 40% |
| **Both (this skill)** | **10K** | **Mixed** | **$2.70** | **70%** |

---

## 🔒 Security

All scripts are **local-only** — no network calls, no subprocess spawning, no system modifications. See [SECURITY.md](SECURITY.md) for full per-script audit.

Verify integrity:
```bash
cd ~/.openclaw/skills/openclaw-token-optimizer
sha256sum -c .clawhubsafe
```

Quick audit (should return nothing):
```bash
grep -r "urllib\|requests\|socket\|subprocess\|curl\|wget" scripts/
```

---

## 📜 Changelog

See [CHANGELOG.md](CHANGELOG.md) for full version history.

**v1.4.2** — Security scanner fixes (provenance, optimize.sh manifest, SECURITY.md)  
**v1.4.1** — `.clawhubignore` added (fixes public visibility)  
**v1.4.0** — Native OpenClaw 2026.2.15 features (session pruning, bootstrap limits, cache TTL)  
**v1.3.3** — Correct display name on ClawHub  
**v1.3.2** — Security audit, SECURITY.md, .clawhubsafe manifest  

---

## 🔗 Links

- **ClawHub:** https://clawhub.ai/Asif2BD/openclaw-token-optimizer
- **GitHub:** https://github.com/Asif2BD/OpenClaw-Token-Optimizer
- **OpenClaw Docs:** https://docs.openclaw.ai
- **License:** Apache 2.0
- **Author:** [Asif2BD](https://github.com/Asif2BD)
