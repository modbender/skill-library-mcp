# Outreach Draft: pskoett / self-improving-agent Collaboration
> Status: DRAFT — review before posting. Do NOT post as-is.
> Created: 2026-02-18

---

## GitHub Discussion / Issue Message

**Title:** Collaboration proposal: self-improving-agent + self-evolving-agent — microscope meets telescope

---

Hi @pskoett 👋

I'm the author of [self-evolving-agent](https://clawhub.io/ramsbaby/self-evolving-agent), and I've been quietly admiring self-improving-agent for a while. With 15,962 downloads you've clearly built something that resonates with a lot of people — congratulations.

I wanted to reach out because I think our two skills are doing genuinely different things, and I've been thinking about how they could work better together.

---

### What each skill does (as I understand it)

**self-improving-agent** (yours): Reactive, session-level quality scoring. When something goes wrong — a failure, a user correction, unexpected behavior — it captures that signal and scores the session. It's a microscope: precise, immediate, per-session.

**self-evolving-agent v4.0** (mine): Proactive, system-level analysis. A weekly cron job reads across *all* sessions, looks for patterns, and proposes concrete changes to `AGENTS.md` — the agent's behavioral constitution. It measures whether proposed changes actually improve things over time. It's a telescope: broad, longitudinal, cross-session.

I don't think we're competing. We're operating at completely different granularities.

---

### Why they're complementary

Your skill answers: *"What went wrong in this session, and how bad was it?"*

Mine answers: *"Across the last 100 sessions, is the agent getting better or worse systemically?"*

The interesting thing is that your quality scores are exactly the kind of signal mine would love to have. Right now, self-evolving-agent infers quality from indirect signals (correction rates, task completion patterns, user sentiment). But if it could aggregate your session-level scores over a rolling window, the system-level analysis would be dramatically more accurate.

---

### Concrete proposal

**1. Mutual cross-recommendation in READMEs**

I'd like to add a "Works great with self-improving-agent" section to my README, and I'd be happy to open a PR to yours suggesting a similar note. No marketing copy — just a clear, honest explanation that the two skills operate at different layers and pair well.

**2. Future integration (longer term)**

If you're open to it, I'd love to explore a lightweight integration where self-improving-agent's quality scores write to a shared log file (e.g., `~/.openclaw/logs/quality-scores.jsonl`), and self-evolving-agent reads that file during its weekly analysis pass. This would require no changes to either skill's core logic — just an agreed-upon schema for the shared file.

Rough schema sketch (not a spec, just a starting point):

```jsonl
{"ts": 1740000000, "session_id": "abc123", "score": 7.2, "trigger": "correction", "skill": "self-improving-agent"}
```

This is entirely optional and something to think about — I'm not trying to rush anything.

---

### What I'm NOT proposing

- No merging, no forks, no dependencies
- No changes to your skill's core behavior
- No asking you to do extra work

Just two authors who built complementary tools, acknowledging that publicly.

---

If this sounds interesting, I'm happy to open a PR with the README section and see what you think. If you'd rather keep things independent, I completely understand — I'll add a unilateral mention in my README and leave it at that.

Either way, thanks for building something genuinely useful. Self-improving-agent is exactly the kind of skill the ecosystem needs.

— ramsbaby

---

---

## PR Description

**Title:** docs: add "Works great with self-improving-agent" section to README

---

### Summary

Adds a short "Pairs well with" section to the README acknowledging that self-improving-agent and self-evolving-agent operate at complementary levels of granularity.

### Motivation

self-improving-agent (by @pskoett) does reactive, per-session quality scoring triggered by failures and corrections. self-evolving-agent does proactive, weekly cross-session analysis and proposes systemic changes to `AGENTS.md`.

These are not competing skills — they're a microscope and a telescope. Users who install both get session-level diagnostics *and* long-term behavioral drift correction. That's worth saying clearly in the README.

### Changes

- Added `## Pairs well with` section to `README.md`
- No functional changes

### README section added

```markdown
## Pairs well with

**[self-improving-agent](https://clawhub.io/pskoett/self-improving-agent)** by @pskoett

self-improving-agent captures per-session quality signals when something goes wrong (corrections, failures, unexpected behavior). self-evolving-agent aggregates patterns across *all* sessions over time and proposes systemic improvements to your agent's behavior.

They operate at different layers:
- self-improving-agent = **microscope** (session-level, reactive)
- self-evolving-agent = **telescope** (system-level, proactive)

Installing both gives you immediate session diagnostics *and* long-term behavioral evolution. They don't conflict — they compound.
```

---
*Draft only — do not merge without author review.*
