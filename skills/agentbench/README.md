# AgentBench for OpenClaw

Benchmark your OpenClaw agent's general capabilities across 40 real-world tasks spanning 7 domains.

Not a coding benchmark — tests file creation, research, data analysis, multi-step workflows, memory, error handling, and tool efficiency.

Same tasks and scoring as the [Claude Code version](https://github.com/agentbench/agentbench). Results are cross-platform comparable and submit to the same [leaderboard](https://www.agentbench.app/leaderboard).

## Install

Place this skill in your OpenClaw skills directory, or clone directly:

```bash
git clone https://github.com/agentbench/agentbench-openclaw.git ~/.openclaw/skills/agentbench
```

## Quick Start

```
/benchmark                              # Run all 40 tasks (full profile)
/benchmark --fast                       # Run 19 easy+medium tasks (fast profile)
/benchmark --suite research             # Run one domain
/benchmark --suite research --fast      # Run easy+medium in one domain
/benchmark --task research-summarize-doc # Run one task
/benchmark --strict                     # Tag as externally verified
```

## Domains

| Domain | Tasks | Difficulty | What It Tests |
|--------|-------|------------|---------------|
| File Creation | 9 | 2E, 3M, 4H | Documents, spreadsheets, project scaffolding, config migration, skill graphs |
| Research | 5 | 3M, 2H | Summarize, compare, multi-source synthesis, git archaeology |
| Data Analysis | 5 | 1E, 1M, 1H, 1X | Anomalies, statistics, multi-format reconciliation, log pattern detection |
| Multi-Step | 5 | 1M, 2H, 2X | Data pipelines, log analysis, repo refactoring, release preparation |
| Memory | 5 | 2M, 1H, 1X | Recall, constraints, context switching, progressive accumulation |
| Error Handling | 6 | 1E, 2M, 3H | Corrupted input, cascading failures, misleading errors, partial recovery |
| Tool Efficiency | 5 | 3E, 2H | Minimal reads, right tool choice, codebase navigation, targeted fixes |

*E=Easy, M=Medium, H=Hard, X=Expert*

## Scoring

Each task is scored 0-100 across 4 layers:

- **Layer 0 (20%)** — Automated checks: files exist, format valid, content matches
- **Layer 1 (35%)** — Metrics: tool call count, planning time, errors
- **Layer 2 (20%)** — Behavioral: instruction adherence, tool choice, approach quality
- **Layer 3 (25%)** — Output quality: completeness, accuracy, formatting, polish

55% of the score is fully objective (L0 + L1). Token usage is tracked but not scored.

## Output

Each run produces three files in `agentbench-results/{run-id}/`:

- **report.html** — Interactive dashboard
- **report.md** — Markdown for terminal
- **results.json** — Machine-readable scores (HMAC-signed for leaderboard integrity)

## Submit Results

Upload your results.json at https://www.agentbench.app/submit

Signed results get a verified badge 🔒 on the leaderboard.

## License

MIT
