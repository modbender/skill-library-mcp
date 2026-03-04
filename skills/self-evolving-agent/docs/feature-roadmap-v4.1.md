# Feature Roadmap — v4.1 / v4.2
> Research Date: 2026-02-18  
> Scope: Competitive analysis + market research → TOP 5 features for self-evolving-agent  
> Method: Code audit (v4.0 scripts), competitor analysis, web research (LangSmith, CrewAI, observability tools 2026)

---

## Executive Summary

v4.0 is a solid foundation: 5-stage pipeline, closed feedback loop, <$0.05/run, human approval gate. But the devil's advocate critique (docs/devils-advocate.md) was right about the core weaknesses:

1. **"It's just grep"** — keyword matching at ~15% FP is still brittle
2. **No visible ROI** — users can't see improvement over time → low retention
3. **Korean-only patterns** — kills 90%+ of global addressable market
4. **Approval fatigue** — weekly Discord messages with no edit-before-apply option
5. **Discord lock-in** — excludes Slack/Telegram/webhook users

The 5 features below directly attack these in priority order. Each is **feasible in 1-2 weeks** with the existing bash/Python stack.

---

## Competitive Context

| Tool | What they do well | What they miss |
|------|------------------|----------------|
| **self-improving-agent** (pskoett v1.0.5) | Hook-based, multi-platform, mature community | Manual logging only, no analysis loop, no benchmark |
| **LangSmith / Langfuse** | Beautiful tracing dashboards, token tracking | General LLM tools — not AGENTS.md-specific |
| **AgentOps** | Real-time monitoring, cost tracking | Cloud-only, expensive, no personal assistant focus |
| **CrewAI observability** | Event emitter for multi-agent pipelines | No feedback loop, no self-improvement |
| **self-evolve** (Be1Human) | Radical autonomy | No human gate, security nightmare |

**The gap nobody fills:** A personal-assistant-specific feedback loop that:  
(a) reads your actual conversation logs, (b) measures improvement over time, (c) shows the history visually, and (d) works for any language/platform.

v4.0 has (a) and (b). v4.1/v4.2 must add (c) and (d).

---

## Feature #1 — Local Web Dashboard

**Priority: P0 | Effort: ~10 days | Target: v4.1**

### What It Does

A lightweight local HTTP server (Python `http.server` + vanilla HTML/Chart.js) that renders:

- **Improvement timeline** — proposals over time, with accept/reject/pending status
- **Pattern frequency chart** — trend lines showing `"다시"`, `"again"`, `"you forgot"` frequency week-by-week
- **Benchmark heatmap** — which proposals were Effective / Neutral / Regressed
- **AGENTS.md diff viewer** — click any proposal to see before/after

Served at `http://localhost:7842` — accessible from browser, no external dependencies.

```
┌───────────────────────────────────────────────────────────┐
│  🧠 Self-Evolving Agent — Dashboard          v4.1        │
├───────────────────────────────────────────────────────────┤
│  📊 Complaint Frequency (12 weeks)                        │
│  ██████░░ "again" / "다시"     22→3  (↓86%)              │
│  █████░░░ "you forgot"         17→8  (↓53%)              │
│  ███░░░░░ "how many times"      8→1  (↓88%)              │
│                                                           │
│  📋 Proposal History                                      │
│  2026-02-17  4 proposals  ✅3 applied  ❌1 rejected      │
│  2026-02-10  2 proposals  ✅2 applied                    │
│                                                           │
│  📈 Benchmark Results                                     │
│  #4 exec-retry rule: ✅ Effective (−45%)                 │
│  #3 log-check rule:  ⏳ Neutral  (+2%) — observe more   │
└───────────────────────────────────────────────────────────┘
```

### Why Users Want It

**Retention is the #1 problem.** Current flow: Discord message → read it → maybe apply → forget. No visible progress = no motivation to keep using it.

LangSmith and Langfuse are the fastest-growing AI tools in 2026 *specifically because* developers can see what's happening. The self-evolving-agent has all the data for a compelling dashboard — it just doesn't surface it.

A GIF of this dashboard running = instant viral marketing material (Reddit, HN, Twitter/X). It's the demo that sells the product.

Market signal: "15 AI Agent Observability Tools in 2026" article exists. Dashboard/observability is the #1 category users search for.

### Implementation Notes

```bash
# New files:
scripts/v4/dashboard-server.py    # Python HTTP server + data aggregator
scripts/v4/start-dashboard.sh     # Wrapper: starts server, opens browser
templates/dashboard.html          # Chart.js + vanilla JS, no CDN needed

# Data sources (already exist):
data/proposals/*.json             # Proposal history
data/benchmarks/*.json            # Effectiveness results
/tmp/sea-v4/analysis-*.json       # Pattern frequency over time
```

```bash
# Usage:
bash scripts/v4/start-dashboard.sh
# → opens http://localhost:7842
# → auto-reloads when new run completes
```

### Estimated Effort

- Backend aggregation script: 3 days
- HTML/Chart.js template: 3 days
- Integration with orchestrator (write dashboard-compatible JSON): 2 days
- Testing + OpenClaw canvas compatibility: 2 days
- **Total: ~10 days**

---

## Feature #2 — English-First Pattern Library + Language Auto-Detection

**Priority: P0 | Effort: ~4 days | Target: v4.1**

### What It Does

Ships English-language default frustration patterns as the primary set, with Korean as an optional locale. Adds automatic language detection from log content so the right pattern library activates without config.

```yaml
# config.yaml (new structure)
analysis:
  language: auto   # auto | en | ko | ja | es
  
  # Auto-detected or manually selected pattern libraries:
  # Each ships as patterns/en.yaml, patterns/ko.yaml, patterns/ja.yaml
```

```yaml
# patterns/en.yaml (new file — ships by default)
complaint_patterns:
  - "you forgot again"
  - "stop doing that"
  - "how many times"
  - "I already told you"
  - "same mistake"
  - "you keep doing"
  - "didn't I say"
  - "you ignored"
  - "why again"
  - "as I mentioned"

exec_retry_signals:
  - "try again"
  - "that didn't work"
  - "still failing"
  - "same error"
```

```yaml
# patterns/ja.yaml (new — community-contributed)
complaint_patterns:
  - "また同じ"
  - "何度言えば"
  - "忘れたの"
  - "さっき言った"
```

### Why Users Want It

**90% of the global OpenClaw market speaks English first.** Korean-only patterns make v4.0 invisible to the vast majority of ClawHub users.

This is not a "nice to have" — it's the single biggest adoption blocker. The market analysis already identified this. The devil's advocate confirmed it. The competitor `recursive-self-improvement` was killed by Chinese-only documentation. We're making the same mistake with Korean defaults.

Language auto-detection removes the config friction: install → works → in your language.

Community contributions: once there's a `patterns/` directory structure, non-English speakers can open PRs with their locale. This is a community flywheel.

### Implementation Notes

```bash
# New files:
patterns/en.yaml    # English patterns (new default)
patterns/ko.yaml    # Korean patterns (current default, now optional)
patterns/ja.yaml    # Japanese (skeleton, community to fill)
patterns/es.yaml    # Spanish (skeleton)
scripts/lib/lang-detect.sh  # Simple language detection via character frequency
```

```bash
# lang-detect.sh logic:
# If >30% of log characters are hangul → ko
# If >20% are CJK (non-hangul) → ja  
# Otherwise → en
# Override with config.yaml language: setting
```

### Estimated Effort

- Write `en.yaml` with 30+ patterns: 1 day (research + test)
- Refactor `ko.yaml` from current hardcoded values: 0.5 days
- `lang-detect.sh` script: 1 day
- Wire into `collect-logs.sh` and `semantic-analyze.sh`: 1 day
- Skeleton `ja.yaml`, `es.yaml` with community instructions: 0.5 days
- **Total: ~4 days**

---

## Feature #3 — Semantic Embedding Analysis (Local, Ollama-Powered)

**Priority: P1 | Effort: ~12 days | Target: v4.2**

### What It Does

Replaces the keyword regex core with embedding-based semantic similarity clustering. Uses Ollama's `nomic-embed-text` model (runs 100% locally, no API cost) to:

1. Embed every user message in the log window into a vector
2. Cluster semantically similar messages using cosine similarity (scipy or pure Python)
3. Identify complaint clusters by proximity to seed complaint vectors
4. Report: "Cluster #3 (12 messages): semantically related to 'agent forgot instructions'"

```
Current (v4.0):            New (v4.2 semantic):
"다시" → hit             "다시", "again", "you forgot", "same thing"
"again" → miss           → All cluster together as semantic group
"you forgot" → miss      → "Complaint cluster: memory failure (14 hits)"
"same thing" → miss      
```

False positive estimate: ~15% (v4.0) → **<8% (v4.2 target)**  
New pattern discovery: None → **Automatic** (clusters emerge without predefined keywords)

### Why Users Want It

The devil's advocate critique was dead-on: `if pattern in sent: count += 1` is 1990s sentiment analysis. Any developer who reads the code will see this immediately and question the entire tool.

Embedding-based analysis is the **defensible moat** that takes 2+ weeks for competitors to replicate (because it requires architecture changes, not just new YAML patterns). It makes the tool genuinely hard to dismiss as "just grep."

Market context: CodeGrok MCP (HackerNews Jan 2026) got massive traction for replacing grep with semantic search. Same concept applied to log analysis is a natural extension. "CodeGrok for AGENTS.md" is the positioning.

Additionally: auto-discovery of new complaint patterns (patterns the user didn't think to add to config.yaml) is a qualitative leap. Users will notice proposals they couldn't have found manually.

### Implementation Notes

```python
# scripts/v4/semantic-analyze-v2.py (Python, replaces bash semantic-analyze.sh)
# Requires: ollama running locally (already common in OpenClaw setups)

import ollama
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def embed(text: str) -> list[float]:
    return ollama.embeddings(model='nomic-embed-text', prompt=text)['embedding']

# Seed vectors for complaint categories
COMPLAINT_SEEDS = [
    "you forgot what I said",
    "you made the same mistake again", 
    "stop doing that repeatedly",
    "I already told you this",
    "why did you ignore my instructions",
]

def classify_message(msg: str, threshold: float = 0.75) -> str | None:
    msg_vec = np.array(embed(msg))
    for seed in COMPLAINT_SEEDS:
        seed_vec = np.array(embed(seed))  # cached after first run
        if cosine_similarity([msg_vec], [seed_vec])[0][0] > threshold:
            return "complaint"
    return None
```

```bash
# Graceful degradation: if Ollama not available → fall back to v4.0 keyword mode
# DRY_RUN=true always uses keyword mode (no model required)
```

### Estimated Effort

- Python embedding script (ollama integration): 3 days
- Seed vector design + calibration (tuning threshold): 3 days
- Caching layer (don't re-embed same messages): 2 days
- Integration with orchestrator + JSON output format: 2 days
- Fallback to keyword mode when ollama unavailable: 1 day
- Testing + FP rate validation: 1 day
- **Total: ~12 days**

### Dependencies

- Ollama installed and running (optional but recommended)
- `pip install numpy scikit-learn` (or pure Python cosine similarity fallback)
- `nomic-embed-text` model pulled (`ollama pull nomic-embed-text`)

---

## Feature #4 — CLI Approval Workflow (`sea` command)

**Priority: P1 | Effort: ~7 days | Target: v4.1**

### What It Does

A `sea` CLI command that replaces the "type a message in Discord" approval flow with a proper terminal-based workflow:

```bash
# List pending proposals
$ sea status
🧠 Self-Evolving Agent — 3 proposals pending

#1 [HIGH]  exec retry limit rule           — 2026-02-17
#2 [MED]   memory compaction warning       — 2026-02-17
#3 [LOW]   discord formatting rule update  — 2026-02-17

# Preview a proposal (full diff)
$ sea show 1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Proposal #1: exec retry limit rule [HIGH]
Evidence: 405 retry events, max 119 consecutive
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BEFORE: No rule for consecutive exec failures

AFTER (add to AGENTS.md):
+ If same exec command fails 3× consecutively:
+   1. Report error to user immediately
+   2. Second attempt must use different approach  
+   3. Third failure → STOP + request manual help

# Approve as-is
$ sea approve 1
✅ Proposal #1 applied to AGENTS.md (git commit created)

# Approve with inline edit (opens $EDITOR)
$ sea approve 1 --edit
[opens EDITOR with diff pre-loaded — user edits then saves]
✅ Proposal #1 applied (user-modified) to AGENTS.md

# Reject with reason
$ sea reject 1 "exec retries are normal in my workflow"
❌ Proposal #1 rejected — logged to data/rejected-proposals.json
```

### Why Users Want It

**Approval fatigue is the #2 retention killer** (after generic proposals). The current Discord-based flow has too many steps and no editing capability.

Developer users (the target persona) live in the terminal. A `sea approve 1` command is faster, more natural, and supports the "edit before apply" workflow that power users want — equivalent to reviewing a PR before merging.

CrewAI and LangGraph users are accustomed to "review → approve → merge" flows. The `sea` CLI mirrors this familiar pattern. It's also easier to demo and screenshot.

The `--edit` flag directly addresses the fear of "what if the proposal is slightly wrong?" — users can fix it before applying, without losing the automation benefit.

### Implementation Notes

```bash
# New files:
scripts/sea.sh           # Main CLI dispatcher
scripts/v4/approve.sh    # Apply proposal → AGENTS.md + git commit
scripts/v4/reject.sh     # Log rejection + update data/

# Installation (add to PATH):
ln -sf ~/openclaw/skills/self-evolving-agent/scripts/sea.sh /usr/local/bin/sea
```

```bash
# sea.sh dispatches subcommands:
case "$1" in
  status)    bash scripts/v4/list-proposals.sh ;;
  show)      bash scripts/v4/show-proposal.sh "$2" ;;
  approve)   bash scripts/v4/approve.sh "$2" "${3:-}" ;;
  reject)    bash scripts/v4/reject.sh "$2" "${@:3}" ;;
  run)       bash scripts/v4/orchestrator.sh ;;
  dashboard) bash scripts/v4/start-dashboard.sh ;;
esac
```

```bash
# approve.sh:
# 1. Load proposal JSON from data/proposals/
# 2. If --edit: dump diff to /tmp, open $EDITOR, re-read
# 3. Apply to AGENTS.md (sed/awk insert)
# 4. git add AGENTS.md && git commit -m "sea: apply proposal #N"
# 5. Update proposal status to "applied"
```

### Estimated Effort

- `sea.sh` dispatcher + subcommand structure: 1 day
- `sea status` + `sea show`: 1.5 days
- `sea approve` (direct apply + git commit): 2 days
- `sea approve --edit` (editor integration): 1.5 days
- `sea reject` + rejection logging: 1 day
- **Total: ~7 days**

---

## Feature #5 — Multi-Platform Delivery (Slack / Telegram / Webhook)

**Priority: P2 | Effort: ~5 days | Target: v4.2**

### What It Does

Adds delivery targets beyond Discord so teams using Slack, Telegram, or custom webhooks can receive weekly proposals:

```yaml
# config.yaml
delivery:
  mode: discord           # discord | slack | telegram | webhook | file
  discord_channel: ""     # existing
  slack_webhook: ""       # new: Slack Incoming Webhook URL
  telegram_chat_id: ""    # new: Telegram bot chat ID
  telegram_bot_token: ""  # new
  webhook_url: ""         # new: generic HTTP POST endpoint
  output_file: ""         # new: write proposal.md to a file path (no network)
```

```bash
# synthesize-proposal.sh delivery section (new):
case "$DELIVERY_MODE" in
  slack)    post_to_slack "$PROPOSAL_MD" ;;
  telegram) post_to_telegram "$PROPOSAL_MD" ;;
  webhook)  post_to_webhook "$PROPOSAL_MD" ;;
  file)     cp "$PROPOSAL_MD" "$OUTPUT_FILE" ;;
  discord)  # existing behavior
esac
```

The `file` mode is especially useful for CI/CD integrations — write the proposal to a git-tracked file, let CI review it.

### Why Users Want It

**Discord is not universal.** Many OpenClaw users are on Slack (enterprises), Telegram (Europeans, privacy-focused users), or want custom integrations (webhooks → Notion, Linear, GitHub Issues).

Currently, a non-Discord user simply cannot use the skill as intended. This is a hard exclusion that costs installs.

Slack and Telegram are trivial to add (both support simple HTTP POST). The `file` output mode enables a "gitops" workflow where proposals are reviewed as pull requests — which aligns with how many developer teams already operate.

Market size: OpenClaw has 1.5M+ active agents. Even if 20% prefer Slack/Telegram over Discord, that's 300K users currently excluded.

### Implementation Notes

```bash
# New file: scripts/lib/delivery.sh
# Functions: deliver_slack(), deliver_telegram(), deliver_webhook(), deliver_file()

# Slack (Incoming Webhooks):
deliver_slack() {
    local msg="$1"
    curl -sf -X POST "$SLACK_WEBHOOK" \
      -H 'Content-type: application/json' \
      --data "{\"text\": $(echo "$msg" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')}" \
      || echo "Slack delivery failed"
}

# Telegram:
deliver_telegram() {
    local msg="$1"
    curl -sf "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d "chat_id=${TELEGRAM_CHAT_ID}" \
      -d "text=${msg}" \
      -d "parse_mode=Markdown" \
      || echo "Telegram delivery failed"
}
```

```bash
# All delivery methods use || echo fallback — exec never fails
# Credentials stored in config.yaml (gitignored)
```

### Estimated Effort

- `delivery.sh` library with all 4 modes: 2 days
- Integration into `synthesize-proposal.sh`: 1 day
- Config schema update + validation: 0.5 days
- Documentation (setup guide for each platform): 1 day
- Testing with live webhooks: 0.5 days
- **Total: ~5 days**

---

## Priority Matrix

| # | Feature | Priority | Effort | Impact | Target |
|---|---------|----------|--------|--------|--------|
| 1 | **Web Dashboard** | **P0** | 10 days | 🔥 Viral demo, retention fix, #1 adoption driver | v4.1 |
| 2 | **English Pattern Library + Lang Auto-detect** | **P0** | 4 days | 🔥 Opens global market, removes #1 adoption blocker | v4.1 |
| 3 | **Semantic Embedding Analysis** | **P1** | 12 days | 🧠 Defensible moat, kills "it's just grep" criticism | v4.2 |
| 4 | **`sea` CLI Approval Workflow** | **P1** | 7 days | ⚡ Retention fix, power-user appeal | v4.1 |
| 5 | **Multi-Platform Delivery** | **P2** | 5 days | 📣 Market expansion, removes platform lock-in | v4.2 |

---

## Recommended Build Order

### v4.1 Sprint (5-6 weeks total)
```
Week 1–2:  Feature #2 (English patterns) → immediate global unlock
           + Feature #4 (sea CLI) → better UX before dashboard launch
Week 3–4:  Feature #1 (Dashboard) → needs data from F2+F4 running
Week 5:    Polish, docs, GIF demo, README update for ClawHub
```

### v4.2 Sprint (3-4 weeks)
```
Week 1–2:  Feature #3 (Semantic embeddings) → requires Ollama setup docs
Week 3:    Feature #5 (Multi-platform delivery) → quick win
Week 4:    Integration testing, community pattern library PR campaign
```

---

## Why These 5 Beat the Alternatives

**Not included: Advanced causal inference** — too high effort (6+ weeks), research-level ML, not feasible in 1-2 week chunks.

**Not included: Auto-apply without approval** — violates the core safety principle. Would harm trust and ClawHub safety perception. self-evolve tried this; it's positioned as dangerous.

**Not included: GitHub Issues integration** — too niche for core roadmap, better as a community plugin.

**The real differentiator combination:**  
Dashboard (you can SEE progress) + Semantic analysis (it actually UNDERSTANDS) + English support (GLOBAL reach) + CLI approval (DEVELOPER-FRIENDLY UX)  

This combination is genuinely hard to replicate quickly. self-improving-agent would need to add all 4 of these to match — that's 2+ months of work for a competitor, while we ship v4.1 in 6 weeks.

---

## Appendix: Market Signals Observed

- LangSmith, Langfuse, AgentOps, Maxim all grew >200% in 2025 — **observability is the market**
- CrewAI added event emitter for observability in latest release — competitors see the demand
- Darwin Gödel Machine (Sakana AI) got massive press in 2025 — "AI rewriting itself" is a hot topic, riding the wave is smart
- CodeGrok MCP (HN Jan 2026) validated "semantic search > grep" positioning — proof that the embedding pitch works
- claude-flow (GitHub, ranked #1 agent framework) uses CLAUDE.md as governance — confirms the AGENTS.md pattern is mainstream, not niche
- r/LocalLLaMA "Self-Improvement Flywheel" thread requested exactly: quality scorers, immediate feedback loops, compounding system prompts — our v4.1 roadmap hits all three

---

*Research complete. Recommend starting with Feature #2 (English patterns, 4 days) as the fastest adoption unlock, followed by Feature #1 (Dashboard) for the viral demo moment.*
