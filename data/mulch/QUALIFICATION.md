# Mulch Self Improver — Features, benefits & qualification

Use this to qualify fit: who it’s for, what problems it solves, and what you get.

---

## Pain points (problems we solve)

- **Agents forget across sessions** — Patterns and fixes discovered yesterday are lost today; every session starts from zero.
- **No single source of project expertise** — Knowledge lives in chat history, docs, or people’s heads; agents can’t reliably ground in “what this project learned.”
- **More hallucination** — Without project-specific grounding, agents guess conventions, repeat past mistakes, or suggest wrong approaches.
- **Same mistakes repeated** — Failures and workarounds aren’t recorded in a queryable way, so the same errors recur.
- **Slow onboarding** — New agents (or teammates) don’t inherit accumulated learnings; context has to be re-explained.
- **Scattered or ad‑hoc learnings** — Markdown logs or notes don’t scale, aren’t structured, and are hard to search or reuse.

**Qualification:** If the prospect cares about agent memory, consistency, fewer repeated errors, or team-wide expertise, the Mulch Self Improver is a fit.

---

## Benefits

- **Better and more consistent coding** — Agents follow recorded conventions, decisions, and resolutions instead of guessing.
- **Improved experience** — Less back-and-forth correction; agents “remember” project rules and past fixes.
- **Less hallucination** — Expertise is grounded in `.mulch/` and optional promotion to CLAUDE.md / AGENTS.md / SOUL.md / TOOLS.md.
- **Expertise compounds** — Each session can read (`mulch prime`) and write (`mulch record`); knowledge accumulates over time.
- **Works with any agent** — Mulch is a passive CLI layer; no LLM inside. Use from Cursor, Claude Code, OpenClaw, Codex, etc.
- **Git-tracked, team-wide** — `.mulch/` lives in the repo; clone and others get the same expertise; merge-friendly (append-only JSONL).
- **Structured and queryable** — Record types (failure, convention, decision, pattern, guide, reference), domains, and `mulch search` / `mulch query` so agents find the right context.

---

## Features

| Feature | Description |
|--------|-------------|
| **Mulch as single learning store** | All learnings in `.mulch/` via `mulch record`; no separate `.learnings/` markdown. |
| **Session priming** | `mulch prime` at session start loads project expertise into context (full or by domain). |
| **Typed records** | failure, convention, pattern, decision, reference, guide — with optional tags, linking, evidence. |
| **Domains** | Split expertise by area (e.g. api, database, testing) for focused context. |
| **Search & query** | `mulch search "..."` (BM25), `mulch query [domain]`, `mulch status`, `mulch ready`. |
| **Promotion path** | Proven patterns → CLAUDE.md, AGENTS.md, SOUL.md, TOOLS.md; `mulch onboard` for snippets. |
| **OpenClaw hook** | Bootstrap reminder injects `SELF_IMPROVEMENT_REMINDER.md` (main session only; sub-agents skipped). |
| **Optional scripts** | activator.sh, error-detector.sh for reminder/error triggers; extract-skill.sh for skill extraction. |
| **Mulch provider hooks** | `mulch setup cursor` (or claude, codex, etc.) for provider-specific reminders. |
| **Robust docker-test** | Single Docker run validates Mulch CLI, hook behavior, scripts, and SKILL.md. |
| **Benchmark vs [Self Improving Agent — Rank #2 on ClawHub](https://clawhub.ai/pskoett/self-improving-agent)** | `docker run … benchmark`: **total efficiency gain ~27.5% fewer chars** when session + troubleshooting + style/memory are all used (3792 vs 5233 chars). By area: session ~14% less; troubleshooting ~54% fewer chars (559 vs 1215); style & memory ~33% fewer chars (757 vs 1136). See [BENCHMARK.md](BENCHMARK.md). |

---

## Who it’s for (qualification)

- **Teams using AI coding agents** (Cursor, Claude Code, OpenClaw, Codex, etc.) and wanting session-to-session memory.
- **Projects that accumulate non-obvious learnings** — workarounds, conventions, failure resolutions — that should be reused.
- **Orgs that want less hallucination and more consistency** by grounding agents in project expertise.
- **Anyone already considering or using [Mulch](https://github.com/jayminwest/mulch)** — this skill is the “self-improvement” workflow on top of Mulch (record on failures/corrections, prime at start, promote when proven).

---

## Quick qualification checklist

- [ ] Do they use AI coding agents in a project/repo?
- [ ] Do they care about agents “remembering” past fixes and conventions?
- [ ] Do they want fewer repeated mistakes and less hallucination?
- [ ] Are they okay with adding `.mulch/` to the repo and running `mulch prime` / `mulch record` (or provider hooks)?

If yes to the first two and they’re open to Mulch, the skill is a good fit.
