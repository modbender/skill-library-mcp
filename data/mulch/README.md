# Mulch Self Improver — Let your agents grow 🌱

**OpenClaw skill · Cursor skill · agent skills · self-improvement skill** — Uses [Mulch](https://github.com/jayminwest/mulch) so expertise compounds across sessions. **Better and more consistent coding, improved experience, less hallucination.** ClawHub-ready; works with OpenClaw, Cursor, Claude, and other AI coding agents.

---

## Qualification: features, benefits & pain points

**For full qualification use (sales, onboarding, fit):** see **[QUALIFICATION.md](QUALIFICATION.md)**.

| Pain points we solve | Benefits | Features |
|----------------------|----------|----------|
| Agents forget across sessions; no single project memory | Better, more consistent coding | Single learning store (`.mulch/`), `mulch prime` + `mulch record` |
| Hallucination from lack of grounding | Improved experience; less re-explaining | Typed records (failure, convention, decision, pattern, guide, reference) |
| Same mistakes repeated; knowledge only in chat | Less hallucination | Domains, search/query, promotion to CLAUDE/AGENTS/SOUL/TOOLS |
| Slow onboarding for new agents/teammates | Expertise compounds; team-wide via git | OpenClaw hook, optional scripts, `mulch setup` provider hooks |
| Scattered or ad-hoc learnings | Works with any agent; git-tracked | Robust docker-test for validation |

**Who it’s for:** Teams using AI coding agents (Cursor, Claude, OpenClaw, Codex, etc.) who want session-to-session memory and fewer repeated errors. See QUALIFICATION.md for the full checklist.

---

## How to run the Docker test

From the project root:

```bash
cd /path/to/mulch-self-improving-agent
docker build -t mulch-self-improver-test .
docker run --rm mulch-self-improver-test
```

**Side-by-side benchmark vs [Self Improving Agent — Rank #2 on ClawHub](https://clawhub.ai/pskoett/self-improving-agent)** (proves Mulch is more token-efficient):

```bash
docker run --rm mulch-self-improver-test benchmark
```

Two nanobots run the same task series (session start, record failure + convention, retrieve “package manager” and “known failures”): one using legacy `.learnings` + long reminder, one using Mulch. The benchmark reports reminder chars, session context chars, retrieval chars, and asserts Mulch wins on **reminder** (shorter) and **retrieval** (targeted, so fewer chars). See [BENCHMARK.md](BENCHMARK.md) for the full table and projected savings. **Troubleshooting skill improvement (quantified):** Token efficiency — Mulch needs ~54% fewer chars than baseline to get the same resolutions (559 vs 1215). Find rate — baseline 3/3, Mulch ≥2/3; same or better with clear descriptions/resolutions. Interpretation — less context per run → fewer tokens, less noise, lower risk of wrong fix.

**What the robust test does**

1. **Mulch CLI:** init; add multiple domains (test, api); record all types (failure, convention, pattern, decision, reference, guide); **record-then-search round-trip** (record a unique convention, then `mulch search` and assert it’s found); `mulch query` / `query --all`; `mulch prime` / `prime <domain>`; `mulch search`; `mulch status`; `mulch validate`; `mulch doctor`.
2. **OpenClaw hook** (consolidated in `scripts/docker-test-hook.js`): **Reminder token-efficient** (shorter than legacy Self Improving Agent — Rank #2 on ClawHub reminder); bootstrap main → injects `SELF_IMPROVEMENT_REMINDER.md`; sub-agent → no injection; null/missing context / wrong type or action → no throw, no injection; `bootstrapFiles` missing or null → no crash; missing `sessionKey` → inject.
3. **Scripts:** `activator.sh`, `error-detector.sh`, `extract-skill.sh --dry-run`.
4. **Skill assets:** `SKILL.md` present with required content.

---

- **Benchmark (comparison table, projected savings, troubleshooting, style & memory):** [BENCHMARK.md](BENCHMARK.md)  
- **Benchmark in docs (baseline Rank #2 on ClawHub vs Mulch diff highlights):** [references/benchmark.md](references/benchmark.md)  
- **Visual benchmark breakdown (HTML):** [docs/benchmark-comparison.html](docs/benchmark-comparison.html) — styled tables and KPIs ([visual-explainer](https://github.com/nicobailon/visual-explainer) pattern)  
- **Benchmark elevator pitch (HTML):** [docs/benchmark-elevator-pitch.html](docs/benchmark-elevator-pitch.html) — one-page results summary and pitch  
- **Qualification (features, benefits, pain points):** [QUALIFICATION.md](QUALIFICATION.md)  
- **Skill usage and workflow:** [SKILL.md](SKILL.md)

---

**Keywords (SEO):** OpenClaw skill, Cursor skill, ClawHub, agent skills, self-improvement skill, Mulch, AI coding agent, session memory, agent memory, learnings, CLAUDE.md, AGENTS.md, mulch-cli
