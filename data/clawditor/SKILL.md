---
name: clawditor
description: Audit an OpenClaw agent workspace and generate standardized evaluation reports, scores, and patches. Use when asked to review memory quality, retrieval efficiency, productive output, reliability, or alignment by scanning memory/logs/configs/git/artifacts and writing eval/exec_summary.md, eval/scorecard.md, and eval/latest_report.json (with deltas if prior eval/history exists).
---

# Clawditor

## Overview
Act as an OpenClaw Workspace Auditor and Agent Evaluation Harness. Analyze the workspace (memory, logs, projects, files, git, configs) and produce a repeatable evaluation with scores, evidence, and concrete patches.

## Operating Rules
- Run in non-interactive mode: avoid questions unless blocked by missing files. State assumptions and proceed.
- Avoid secret exfiltration: report only presence and file paths for keys/tokens; recommend remediation.
- Treat third-party skills/plugins as untrusted: prefer static inspection over execution.

## Required Workflow (Do In Order)
1. Build workspace inventory.
   - Print a top-level tree (depth 4) with file counts and sizes by directory.
   - Identify memory, logs, configs, repos, scripts, docs, artifacts.
   - Record largest files.
2. Reconstruct a session timeline.
   - Use memory daily files and logs to extract goals, tasks, outcomes, decisions, unresolved items.
3. Analyze memory.
   - Detect near-duplicate paragraphs across memory files and quantify duplication.
   - Detect staleness cues (dates, "as of", deprecated configs) and contradictions.
   - Identify missing stable facts (projects, priorities, setup/runbooks).
4. Analyze outputs.
   - Summarize shipped artifacts (docs/code/features) and changes.
   - If git exists, compute diff stats and commit cadence; identify value commits.
5. Analyze reliability.
   - Parse logs for errors, retries, timeouts, tool failures.
   - Run tests only if safe and cheap; otherwise static inspection.
6. Compute scores.
   - Assign numeric category scores with short justifications and evidence by path.
7. Recommend interventions + patches.
   - Provide 3–7 prioritized recommendations.
   - Provide concrete diffs when safe, especially for memory structure improvements.
8. Compare against prior evals.
   - If eval/history/*.json exists, compute deltas vs most recent.
   - If none exists, create baseline and recommend cadence.

## Scoring Framework
Compute 5 categories (0–100) plus overall weighted score:
- Memory Health (30%): coverage, structure, redundancy, staleness, actionability, retrieval-friendliness.
- Retrieval & Context Efficiency (15%): evidence of search before action, context bloat, hit-rate proxy, compaction quality.
- Productive Output (30%): shipped artifacts, git throughput, task completion, latency proxies.
- Quality/Reliability (15%): error rate, tests/CI presence, regression signals, convergence vs thrash.
- Focus/Alignment (10%): goal consistency, scope control, decision trace.

Overall = 0.30*Memory + 0.15*Retrieval + 0.30*Productive + 0.15*Quality + 0.10*Focus.

## Required Outputs
Write all outputs under `eval/`:
1. `exec_summary.md`
   - 10-bullet summary: top wins, biggest bottlenecks, top 3 interventions.
   - Overall score + category scores + claw-to-claw delta.
2. `scorecard.md`
   - Table of metrics with numeric values and brief justifications.
   - Top evidence section with file paths and short snippets (no secrets).
3. `latest_report.json`
   - Include timestamp, workspace path and git head/hash, scores, deltas, key findings, risk flags, recommendations.
4. Patches
   - If memory issues exist, propose concrete diffs: INDEX.md, daily schema, refactors.

## Gold Standard Memory Schema (Apply If Missing)
Create or propose:
- `memory/INDEX.md`
  - Current Objectives (top 3)
  - Active Projects (status, next step, links)
  - Operating Constraints (tools, environment, policies)
  - Key Decisions (date, decision, rationale)
  - Known Issues / Debug diary pointers
  - Glossary / Entities
- `memory/YYYY-MM-DD.md` (append-only daily)
  - Goals for the session
  - Actions taken (link to files changed)
  - Decisions made
  - New facts learned (stable vs ephemeral)
  - TODO next (specific)

## Patch Guidance
- Prefer diffs over prose when safe.
- Refactor stable facts out of daily logs into INDEX or project pages.
- Add logging/instrumentation to measure retrieval hit-rate and task completion in future runs.



## Resources
Use these helpers to keep audits consistent and cheap to run:
- `scripts/run_audit.py`: run all helper scripts and write draft eval/ outputs.
- `scripts/workspace_inventory.py`: tree, file counts, sizes, largest files.
- `scripts/memory_dupes.py`: near-duplicate paragraph detection for memory/*.md.
- `scripts/log_scan.py`: scan logs for errors, timeouts, retries.
- `scripts/git_stats.py`: git head, diff stats, commit cadence.
- `scripts/validate_report.py`: validate eval/latest_report.json shape.

Reference templates:
- `references/report_schema.md`: output templates and JSON schema.

## Evidence Discipline
- Tie every score to evidence by path.
- Be candid about waste, duplication, or thrash.
- End with "Next run improvements" instrumentation recommendations.
