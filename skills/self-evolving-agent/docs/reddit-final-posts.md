# Reddit Final Posts — Self-Evolving Agent v4.2

> Status: READY TO POST
> Generated: 2026-02-18
> GitHub: https://github.com/Ramsbaby/self-evolving-agent
> Posting order: r/AI_Agents → r/ClaudeAI → r/LocalLLaMA (same day, 30 min apart)
> Best window: Tuesday–Thursday, 9–11 AM EST
> Visual hook: Upload dashboard screenshot first — dark theme, SVG charts, pattern trend lines

---

## POST 1 — r/AI_Agents

**Flair:** Tool/Project

**Title:**
My AI now has a dashboard to watch itself fail — v4.2 ships a local web UI, `sea` CLI, and 104 tests

---

**Body:** *(~2,700 chars — upload dashboard screenshot as image post, body as link or text)*

[Screenshot: dark dashboard — SVG trend charts showing complaint frequency over 12 weeks, rule effectiveness gauges, proposal history]

TL;DR: Self-evolving-agent scans your AI's chat logs weekly, finds retry loops and repeated mistakes, proposes AGENTS.md rule changes, and now visualizes 12 weeks of improvement trends in a local web dashboard. `sea approve` applies the fix and git commits it. <$0.05/week. Your approval required, always.

---

**What's new in v4.2:**

**Dashboard** (the screenshot above)

```bash
bash dashboard/serve.sh
# → http://localhost:8420/dashboard/
```

Dark theme. SVG charts. Zero npm, zero React, zero external dependencies — flat HTML served locally. Shows complaint pattern trends week-over-week, rule effectiveness (which proposals actually worked vs. didn't), full proposal history with before/after diffs, AGENTS.md health score. This is what "did that fix work?" looks like when you can see it.

**`sea` CLI**

```bash
sea proposals                    # pending list
sea approve 4                    # patches AGENTS.md + git commit
sea reject 4 "too broad"         # logged, fed into next cycle
sea status                       # one-line summary
sea run --stage 2                # rerun just the analysis stage
sea health                       # AGENTS.md structure score
```

No more digging through Discord messages. `sea history` shows everything.

**104 automated tests + CI**

shellcheck on every PR + `test-pipeline.sh` / `test-cli.sh` covering the full 5-stage flow. A self-testing tool that doesn't test itself would be embarrassing.

**Setup wizard**

```bash
bash scripts/setup-wizard.sh
# Non-interactive: --yes --platform slack --lang auto
```

Interactive first-run: picks platform (Discord/Slack/Telegram/webhook), sets language auto-detection, registers the weekly cron.

**Security manifests on every script**

Every `scripts/v4/` file has a SECURITY MANIFEST header: what it reads, what it writes, what external calls it makes. Post-ClawHavoc: you can audit exactly what runs on your machine in 30 seconds. Only `benchmark.sh` hits external APIs, and those are optional.

---

**What it still is (not AGI):**

Detection = shell scripts + heuristics. Proposal drafting = 1 Claude API call/week (~$0.03). Dashboard = flat HTML. The boring-technology stack is intentional — you can read the whole thing in an hour.

Cost: **<$0.05/week.** Human approval required. AGENTS.md is never modified without your explicit action.

**GitHub:** https://github.com/Ramsbaby/self-evolving-agent
MIT. ~1,800 lines of shell. Read it before you run it.

---

**First Comment** *(drop immediately after posting)*

Quick notes for setup:

The 104 tests are split across `test-pipeline.sh` (needs mocked log fixtures in `tests/fixtures/`) and `test-cli.sh` (no real logs needed, runs anywhere). If you're not on OpenClaw, start with `test-cli.sh`.

Language detection is automatic in v4.2 — it checks whether your sessions are mostly Korean or English and applies the right keyword patterns. If it misdetects (mixed setups), override in config.yaml:
```yaml
complaint_patterns:
  auto_detect: false
  language: en
```

Also: Stage 3 (benchmark / "did the fix work?") needs 2 weeks of data before it does anything useful. First run will show proposals but no effectiveness numbers. That's expected — come back next week.

Fastest path: `bash scripts/setup-wizard.sh` handles everything.

---
---

## POST 2 — r/ClaudeAI

**Flair:** Tool/Extension

**Title:**
I automated the "update AGENTS.md based on what Claude keeps getting wrong" loop — v4.2 adds a dashboard to prove the rules are actually working

---

**Body:**

Since Karpathy's CLAUDE.md post, a lot of people started treating their rule files seriously. But there's a problem nobody talks about: how do you know your rules are actually working?

You notice a problem → you update AGENTS.md → it works for a while → you forget. Or: you notice a problem → you forget to update → same problem next month.

I built an automated version of the improvement cycle. v4.2 adds the piece that was missing: a local dashboard that shows whether the rules you wrote are actually reducing the problem.

[Screenshot: dark dashboard — 12 weeks of "you forgot" / "again?" / "반복" complaint frequency, trend lines dropping after rule applications]

---

**The finding that made this worth building:**

Weekly cron. Scans my Claude chat logs. Found this:

```
exec retry events (7-day window):  405
Maximum consecutive retries:        119 (same session, same command)
Repeated heartbeat errors:          18× (same error, 7 days)
```

119 consecutive retries. Claude looping silently on a broken command. I had no idea — I wasn't watching every session in real-time. The tool caught it, proposed this:

```diff
+ ## exec Retry Limit
+
+ Same command fails 3× in a row → STOP.
+ Report error to user. Ask for a different approach. Never retry silently.
```

I approved it. Retry events: 405/week → 12/week. v4.2 shows that trend in the dashboard instead of requiring me to diff logs manually.

---

**v4.2 additions:**

**Dashboard** — `bash dashboard/serve.sh` → localhost. Dark theme, SVG charts, zero external dependencies. Shows 12 weeks of complaint frequency, rule effectiveness (Effective / Neutral / Regressed classification per proposal), proposal history with before/after diffs. The "did that fix actually help?" question now has a visual answer.

**`sea` CLI** — `sea approve <id>` patches AGENTS.md and git commits with the proposal ID as the commit message. `sea reject <id> "reason"` stores the reason and feeds it into the next analysis cycle so the same false positive doesn't resurface. No more approving proposals by replying to Discord messages.

**Security manifests** — every pipeline script documents what it reads, writes, and calls externally. Audit surface: 30 seconds. Relevant post-ClawHavoc for anyone who runs shell scripts from GitHub.

**104 automated tests + CI** — shellcheck + full pipeline tests on every PR. If the feedback loop breaks, tests catch it before you run it.

**Multi-platform delivery** — Discord, Slack, Telegram, or generic webhook. One line in config.yaml.

**Setup wizard** — `bash scripts/setup-wizard.sh` — handles first-run config interactively. `--yes` flag for headless/CI.

---

**What the weekly output looks like:**

```
📋 AGENTS.md Weekly Review — 2026-02-16

🔴 NEW PROPOSALS (2):
   1. exec retry limit [405 events, max 119 consecutive]
   2. heartbeat error suppression [18× same error]

📊 ACTIVE RULE EFFECTIVENESS:
   ✅ exec retry limit (applied 2026-02-09)
      Before: 405 events/week → After: 12 (-97%)
   ⚠️  memory compaction rule (applied 2026-01-26)
      Pattern still present — consider revision
```

AGENTS.md is **never** modified without you running `sea approve`. The proposals come with evidence. You make the call.

---

**Honest limits:**

Detection is keyword matching + structural heuristics, not semantic understanding. False positives sit around ~15% (down from ~40% in v3). Benchmark needs 2 weeks of baseline before it does anything useful. If your logs are sparse, proposals will be generic.

It's not AGI. It's grep with opinions and a dashboard. The "self-evolving" name describes the goal, not the mechanism.

**GitHub:** https://github.com/Ramsbaby/self-evolving-agent
Open source, MIT. ~1,800 lines of shell. Read before running.

---

**First Comment** *(drop immediately after posting)*

One thing I didn't mention in the post: if you run the setup wizard and pick "Discord," you don't need to configure `deliver.sh` — OpenClaw's native cron delivery handles it. The deliver.sh path is only for Slack/Telegram/webhook.

Also worth knowing: the keyword tuning in config.yaml is where most of the signal quality comes from. The defaults cover common English patterns ("you forgot", "again?", "same mistake", "stop doing that") but after your first run, check `sea status` to see which patterns are hitting and add your own. The tool is only as smart as the patterns you define for your specific failure modes.

Stage 3 effectiveness data shows up on run #2 (week 2). First run: proposals only, no before/after comparison. That's expected.

---
---

## POST 3 — r/LocalLLaMA

**Flair:** Discussion / Tools

**Title:**
Local-first AI observability for my Claude agent: dark dashboard, $0.05/week, zero cloud, 104 tests — v4.2

---

**Body:**

[Screenshot: dark web dashboard at localhost:8420 — SVG line charts showing complaint frequency declining over 12 weeks, rule effectiveness gauges, proposal history table]

I run Claude locally via OpenClaw and had zero visibility into what was going wrong at a system level. Not "this session had a bug" — the stuff that compounds across weeks. Retry loops you miss because you're not watching every session. The same error firing 18 times before you realize it's structural.

Self-evolving-agent v4.2 is the observability layer I built for it.

---

**Architecture (local-first by design):**

```
Your local logs (~/.openclaw/logs/)
    ↓
Stage 1: collect-logs.sh     — pure shell, reads local files only
Stage 2: semantic-analyze.sh — heuristics + keyword matching
Stage 3: benchmark.sh        — this week vs. last week per active rule
Stage 4: measure-effects.sh  — did past proposals actually reduce errors?
Stage 5: synthesize.sh       — 1× Claude API call (~8K tokens, ~$0.03)
    ↓
Local dashboard + your approval gate
```

One API call per week. Everything else runs locally. No cloud observability SaaS. No data leaving your machine except the synthesis call — and that's just anonymized pattern counts and proposed rule text, not your actual conversation logs.

---

**v4.2 new stuff:**

**Local web dashboard**

```bash
bash dashboard/serve.sh
# → http://localhost:8420/dashboard/
```

Dark theme. SVG charts. Zero npm, zero React, zero external dependencies. Just Python `http.server` + flat HTML. Shows 12 weeks of trend data, rule effectiveness (Effective / Neutral / Regressed per proposal), proposal history with before/after diffs, AGENTS.md health score.

**`sea` CLI:**

```bash
sea proposals                    # pending list
sea approve 4                    # patches rules file + git commit
sea reject 4 "false positive"    # logged, fed back into next cycle
sea run --stage 2                # rerun just analysis
sea status                       # one-line summary
sea health                       # structure + coverage score
```

**104 automated tests:**

shellcheck CI on every PR + `test-pipeline.sh` / `test-cli.sh` covering the full 5-stage flow. Fixtures in `tests/fixtures/` for offline runs. If your monitoring tool is untested, you've just added something else to debug.

**Security manifests:**

Every script in `scripts/v4/` has a SECURITY MANIFEST header:

```bash
# SECURITY MANIFEST
# Reads:    ~/.openclaw/logs/*.log, data/proposals/*.json
# Writes:   /tmp/sea-v4/analysis.json
# Network:  none
```

Audit what runs on your machine in 30 seconds. Only `benchmark.sh` touches external APIs (GitHub star count, ClawHub metrics) — and both are optional, gated by config, skipped on failure.

**Setup wizard:**

```bash
bash scripts/setup-wizard.sh
# Non-interactive: --yes --platform slack --lang auto
```

Interactive first-run. Picks your platform, sets language auto-detection (Korean/English based on session content), registers the weekly cron.

**Multi-platform delivery** — Slack Incoming Webhook, Telegram Bot API, generic JSON POST, or Discord. One config.yaml line.

---

**Can you replace the Claude synthesis call with a local Ollama model?**

Yes, with some work. `synthesize-proposal.sh` makes a single curl call to the Anthropic API. You could swap the endpoint for Ollama — the prompt is straightforward (structured JSON in, Markdown diff out). Works better with 70B+ models; smaller models produce generic proposals. If you build it, the synthesis call is isolated enough that a `--local-llm` flag would be a clean PR.

---

**Cost breakdown:**

| Item | Weekly cost |
|------|-------------|
| Claude Sonnet synthesis (~8K tokens) | ~$0.03 |
| Local pipeline (5 stages) | $0.00 |
| Dashboard hosting | $0.00 |
| Storage (JSON proposal history) | ~2MB/month |
| **Total** | **<$0.05/week** |

For 12 months: ~$2.60 in API costs. Or swap to local Ollama and get it to ~$0.00.

---

**What it doesn't do:**

- No real-time tracing (LangSmith territory)
- Only reads OpenClaw log format (not generic LangChain/LlamaIndex traces)
- Requires 2 weeks of baseline before the benchmark stage does anything useful
- Sparse logs = generic proposals

**GitHub:** https://github.com/Ramsbaby/self-evolving-agent
MIT. All shell, ~1,800 lines. No dependencies. Read it before running it — the security manifests make that fast.

---

**First Comment** *(drop immediately after posting)*

For local Ollama users specifically: the synthesis prompt is in `scripts/v4/synthesize-proposal.sh`, around line 80. It's a single curl call with a structured JSON context object (pattern counts, benchmark results, recent proposals) and asks for a Markdown diff output.

Tested with Qwen2.5-72B and it works reasonably well. Smaller models (7B-13B) tend to produce "consider improving your rules" type proposals without specifics — not useful. The structured heuristic data in Stage 2's output is what gives the model enough signal to write a concrete diff.

If you adapt it, set `SEA_SYNTHESIS_ENDPOINT` env var and the script will use that instead of the Anthropic API — I left the hook in for exactly this. PR welcome.

Also: the dashboard `build-index.sh` script needs to run after each pipeline execution to refresh the data files the frontend reads. It's called automatically by `orchestrator.sh` but if you run stages manually, run `bash dashboard/build-index.sh` after Stage 5.

---
---

## Posting Checklist

- [ ] Dashboard screenshot exported (dark theme, shows trend lines declining)
- [ ] GitHub README has screenshot embedded (visitors need to see it before clicking)
- [ ] r/AI_Agents posted first (9–11 AM EST, Tue–Thu)
- [ ] r/ClaudeAI posted 30 min later
- [ ] r/LocalLLaMA posted 30 min after that
- [ ] First comment dropped on each within 2 minutes of posting
- [ ] Cross-link the posts in first comments if r/AI_Agents gets traction

## Do Not Say

- "Revolutionary" / "game-changing"
- "Full feedback loop" (Stage 3 is real but still maturing)
- "AI self-reflection" (it's heuristics — say that plainly)
- "Works great out of the box" (keyword tuning required)
- "Self-improving" without clarifying that the AI proposes, you improve
