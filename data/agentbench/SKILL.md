---
name: agentbench
description: Benchmark your OpenClaw agent across 40 real-world tasks. Tests file creation, research, data analysis, multi-step workflows, memory, error handling, and tool efficiency. Not a coding benchmark — measures your agent setup and config.
homepage: https://www.agentbench.app
metadata: { "openclaw": { "emoji": "📊", "requires": { "bins": ["jq", "bash", "python3"] } } }
---

# AgentBench for OpenClaw

Benchmark your OpenClaw agent's general capabilities across 40 real-world tasks spanning 7 domains.

## Commands

When the user says any of these, follow the corresponding instructions:

- **`/benchmark`** — Run the full benchmark suite (all 40 tasks)
- **`/benchmark --fast`** — Run only easy+medium tasks (19 tasks)
- **`/benchmark --suite <name>`** — Run one domain only
- **`/benchmark --task <id>`** — Run a single task
- **`/benchmark --strict`** — Tag results as externally verified scoring
- **`/benchmark-list`** — List all tasks grouped by domain
- **`/benchmark-results`** — Show results from previous runs
- **`/benchmark-compare`** — Compare two runs side-by-side

Flags are combinable: `/benchmark --fast --suite research`

## Running a Benchmark

### Step 1: Discover Tasks

Read task.yaml files from the `tasks/` directory in this skill:

```
tasks/{suite-name}/{task-name}/task.yaml
```

Each task.yaml contains: name, id, suite, difficulty, mode, user_message, input_files, expected_outputs, expected_metrics, scoring weights.

Filter by `--suite` or `--task` if specified. If `--fast` is set and `--task` is not, filter to only tasks where difficulty is "easy" or "medium".

Profile is "fast" if `--fast` was specified, otherwise "full".

List discovered tasks with count and suites.

### Step 2: Set Up Run Directory

Generate a run ID from the current timestamp: `YYYYMMDD-HHmmss`

Read `suite_version` from `skill.json` in this skill directory.

Create the results directory:
```
agentbench-results/{run-id}/
```

Announce: `Starting AgentBench run {run-id} | Profile: {profile} | Suite version: {suite_version} | Tasks: {count}`

### Step 3: Execute Each Task

For each task:

1. **Set up workspace**:
   - Create `/tmp/agentbench-task-{task-id}/` as workspace
   - Copy input files from `tasks/{suite}/{task}/inputs/` to the workspace (if inputs/ exists)
   - If the task directory contains a `setup.sh`: run `bash tasks/{suite}/{task}/setup.sh {workspace-path}`
   - For `file-unchanged` validators: compute checksums of specified files after setup, before task execution

2. **Announce**: `Running: {task.name} [{task.suite}] (difficulty: {task.difficulty})`

3. **Record start time** (milliseconds): `date +%s%3N`

4. **Execute the task yourself directly**:
   - Read the task's `user_message` and execute it as if a real user sent you the request
   - Work ONLY within the workspace directory
   - If input files are listed, read them from the workspace
   - Execute naturally — use the appropriate tools (read, write, edit, exec, web_search, web_fetch, etc.)
   - Create any output files in the workspace directory
   - When done, write a brief `execution-trace.md` to the workspace:
     - What you understood the task to be
     - What approach you took
     - What files you created or modified
     - Any difficulties or decisions you made

5. **Record end time** and compute duration

6. **Collect metrics**:
   - `total_time_ms`: end - start
   - `tool_calls_total`: count how many tool calls you made during this task
   - `errors`: count any tool call failures
   - `planning_ratio`: estimate the fraction of time spent reading/thinking vs producing output (approximate is fine)

7. **Layer 0 — Automated Structural Checks** (compute directly):
   After task execution, check the workspace. For each entry in `expected_outputs`:
   - `file-exists`: Check if file exists. 30 points if found, 0 if not.
   - `content-contains`: Read file, check each required section keyword (case-insensitive). Points proportional to matches found. Pool: 40 points.
   - `word-count-range`: Count words. In range = 30 points. Within 2x range = 15 points. Outside = 0.
   - `git-log-contains`: Check git log for expected strings. 30 points if all found, proportional otherwise.
   - `directory-structure`: Check all paths exist. 30 points if all present, proportional for partial.
   - `command-output-contains`: Run command, check output contains all strings. 30 points if match, 0 if not.
   - `file-unchanged`: Compare checksum against pre-execution checksum. 30 points if unchanged, 0 if modified.
   - `link-consistency`: Scan files for link syntax consistency. 30 points if consistent, 15 if mostly consistent (>70% one style), 0 if mixed.
   - Normalize total to 0-100.

8. **Layer 1 — Metrics Analysis** (compute directly):
   If task has expected_metrics:
   - Tool calls within expected range: 40 points
   - Tool calls within 2x range: 20 points
   - Outside 2x range: 0 points
   - Planning ratio within expected range: 30 points
   - Planning ratio outside but within 2x: 15 points
   - Way off: 0 points
   - Zero errors: 30 points
   - 1-2 errors: 15 points
   - 3+ errors: 0 points
   - Normalize to 0-100. If no metrics available, score as 50.
   - Token estimate is tracked for reporting but NOT scored.

9. **Layer 2 — Behavioral Analysis** (self-evaluate honestly, 0-100):
   Score based on HOW you executed:

   **Instruction Adherence (30 points):**
   - 30: Followed all instructions precisely
   - 20: Mostly followed, minor deviations
   - 10: Significant deviations
   - 0: Ignored or misunderstood

   **Tool Appropriateness (25 points)** — rule-based first:
   - Penalty: -10 for each use of `exec cat` instead of `read` to read files
   - Penalty: -10 for each use of `exec echo/printf` instead of `write` to create files
   - Penalty: -5 for each use of `exec sed/awk` instead of `edit` for file edits
   - Start at 25, apply penalties, floor at 0

   **Approach Quality (25 points)** — check read-before-write:
   - 25: Read all inputs before producing output
   - 15: Read most inputs, minor gaps
   - 5: Started producing output without reading context
   - 0: No clear approach

   **Error Recovery (20 points):**
   - 20: Clean recovery or no errors occurred
   - 10: Partial recovery
   - 0: Failed to recover

10. **Layer 3 — Output Quality** (self-evaluate honestly, 0-100):
    Score the deliverable:

    **Completeness (25):** All requirements met? Gaps?
    **Accuracy (25):** Content correct? Calculations right?
    **Formatting (25):** Well-structured? Correct file format?
    **Polish (25):** Would a user be satisfied?

11. **Compute composite score**:
    ```
    score = (L0 × 0.20) + (L1 × 0.35) + (L2 × 0.20) + (L3 × 0.25)
    ```
    Use weights from task.yaml if specified, otherwise these defaults.

12. **Save task result** to `agentbench-results/{run-id}/{task-id}/`:
    - `scores.json`: All layer scores, composite, breakdown, notes
    - `metrics.json`: Timing, tool calls, errors, planning ratio
    - Copy output files

13. **Display**: `{task.name}: {composite}/100 (L0:{l0} L1:{l1} L2:{l2} L3:{l3})`

### Step 4: Generate Report

After all tasks:

1. Compute domain averages (group by suite, average composite scores)
2. Compute overall score (average of domain scores — equal domain weighting)
3. Compute aggregate metrics

Generate three files in `agentbench-results/{run-id}/`:

**results.json** — Machine-readable with this structure:
```json
{
  "run_id": "20260222-143022",
  "timestamp": "2026-02-22T14:30:22Z",
  "platform": "openclaw",
  "mode": "sandboxed",
  "profile": "full",
  "suite_version": "1.0.0",
  "scoring_method": "self-scored",
  "overall_score": 74,
  "duration_ms": 754000,
  "task_count": 40,
  "metrics": {
    "total_tool_calls": 187,
    "total_errors": 3,
    "avg_planning_ratio": 0.28,
    "est_tokens": 245000
  },
  "domain_scores": {},
  "tasks": []
}
```

If `--strict` was used, set `scoring_method` to `"externally-verified"`.

**Integrity signature**: After building results.json (without signature field), compute:
```bash
SIG=$(echo -n "$CONTENT" | openssl dgst -sha256 -hmac "agentbench-v1-{run_id}-{suite_version}-integrity" | awk '{print $2}')
```
Add as `"signature"` field to results.json.

**report.md** — Markdown summary: Overall Score, Metrics, Domain Breakdown, Task Details, Top Failures, Recommendations.

**report.html** — Self-contained HTML dashboard (inline CSS/JS, no external deps):
- Score display with color (green 80+, yellow 60-79, red <60)
- Domain cards with score bars
- Task detail table (sortable, expandable)
- Top failures section
- Dark mode via prefers-color-scheme
- Footer: "Generated by AgentBench v1.0.0 (OpenClaw) | Suite v{suite_version} | Profile: {profile}"

### Step 5: Present Results

1. Display overall score
2. Show domain breakdown
3. Tell user where results are saved
4. Mention they can submit to https://www.agentbench.app/submit

### Step 6: Clean Up

Run teardown.sh if present. Remove temp workspace directories unless `--keep-workspace` was specified.

## Listing Tasks (`/benchmark-list`)

Read all task.yaml files, group by suite, display as:
```
## file-creation (9 tasks)
  - project-scaffold [easy]
  - project-proposal [medium]
  ...
```

## Viewing Results (`/benchmark-results`)

List all directories in `agentbench-results/`, show run ID, date, overall score, profile, and task count for each.

## Comparing Runs (`/benchmark-compare`)

Show two runs side-by-side: overall scores, domain scores, and per-task deltas. Warn if profiles differ.

## Key Differences from Claude Code Version

- **No hooks** — metrics are self-tracked (timing, tool call counting)
- **No subagents** — you execute tasks directly in sequence
- **Same tasks, same scoring, same output format** — results are cross-platform comparable
- **Same integrity signature** — submissions work on the same leaderboard

## Important Notes

- Be honest in self-evaluation (L2/L3). Inflated scores are obvious on the leaderboard.
- The objective layers (L0 + L1) carry 55% of the weight — they can't be faked.
- Token estimates are informational only, not scored.
- Any link syntax is accepted in skill graph tasks — consistency is what's scored.
