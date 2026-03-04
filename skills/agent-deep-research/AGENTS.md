# Agent Briefing: agent-deep-research

Structured reference for AI agents. Minimal prose, maximum signal.

## Quick Start

```bash
# Check if configured
uv run {baseDir}/scripts/onboard.py --check

# Get full capabilities manifest (JSON)
uv run {baseDir}/scripts/onboard.py --agent
```

## Capabilities

| Command | Script | What It Does | When to Use |
|---------|--------|-------------|-------------|
| `research start` | `scripts/research.py` | Launch deep research job | User needs comprehensive analysis of a topic |
| `research status` | `scripts/research.py` | Check research progress | After non-blocking start, before polling complete |
| `research report` | `scripts/research.py` | Save completed report | Need to retrieve results from a finished job |
| `store create` | `scripts/store.py` | Create file search store | Building a persistent document collection |
| `store query` | `scripts/store.py` | Query a store (RAG) | Quick Q&A against uploaded documents |
| `store list` | `scripts/store.py` | List all stores | Discovering available stores |
| `store delete` | `scripts/store.py` | Delete a store | Cleanup |
| `upload` | `scripts/upload.py` | Upload files to store | Adding documents to an existing store |
| `state show` | `scripts/state.py` | View workspace state | Checking tracked IDs, stores, history |
| `state clear` | `scripts/state.py` | Reset workspace state | Starting fresh |
| `onboard` | `scripts/onboard.py` | Setup wizard / capabilities | First run, config check |

## Decision Tree

### "I need to research a topic"

```
Is there local context (files/code) to ground the research?
  YES -> Do you want to estimate cost first?
    YES -> uv run {baseDir}/scripts/research.py start "question" --context ./path --dry-run
    NO  -> uv run {baseDir}/scripts/research.py start "question" --context ./path --output report.md
  NO  -> uv run {baseDir}/scripts/research.py start "question" --output report.md
```

### "I need to ask about uploaded documents"

```
Is the question simple/focused?
  YES -> uv run {baseDir}/scripts/store.py query <store-name> "question"
  NO (need deep analysis) -> uv run {baseDir}/scripts/research.py start "question" --store <name> --output report.md
```

### "I want non-blocking research"

```
1. Start: RESULT=$(uv run {baseDir}/scripts/research.py start "question")
2. Extract ID: ID=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
3. Check: uv run {baseDir}/scripts/research.py status "$ID"
4. Save: uv run {baseDir}/scripts/research.py report "$ID" --output-dir ./output
```

### "I need to build a document store"

```
1. Create: STORE=$(uv run {baseDir}/scripts/store.py create "name")
2. Upload: uv run {baseDir}/scripts/upload.py ./docs <store-name> --smart-sync
3. Query:  uv run {baseDir}/scripts/store.py query <store-name> "question"
4. Research: uv run {baseDir}/scripts/research.py start "question" --store <name>
```

## Common Workflows

### 1. One-shot research with file context

```bash
uv run {baseDir}/scripts/research.py start "How does the auth system work?" \
  --context ./src --output report.md
```

Context store is created, files uploaded, research grounded, store cleaned up automatically.

### 2. Cost estimate before committing

```bash
uv run {baseDir}/scripts/research.py start "Analyze security architecture" \
  --context ./src --dry-run
```

Returns JSON cost estimate without starting research.

### 3. Structured output for downstream processing

```bash
uv run {baseDir}/scripts/research.py start "Deep analysis" \
  --output-dir ./research-output 2>/dev/null
```

Produces `research-<id>/` directory with `report.md`, `metadata.json`, `interaction.json`, `sources.json`. Compact JSON summary on stdout.

### 4. Follow-up research

```bash
uv run {baseDir}/scripts/research.py start "Dive deeper into finding #3" \
  --follow-up <previous-interaction-id> --output followup.md
```

## Important: Blocking Behavior

When `--output` or `--output-dir` is used, the command **blocks until research completes** (typically 2-10 minutes, up to 30+ for deep research). This is by design -- the report is only written after the Gemini API returns results.

**DO NOT** background the command with shell `&` -- this detaches the process and you lose the output. Instead:
- Use your agent framework's native background execution (e.g., `run_in_background: true` in Claude Code's Bash tool)
- Or use non-blocking mode (no `--output` flag), which returns immediately with `{"id": "...", "status": "in_progress"}`, then poll with `status` and retrieve with `report --output`

**Non-blocking pattern** (recommended for agent use):
```bash
# 1. Start (returns immediately)
RESULT=$(uv run {baseDir}/scripts/research.py start "question" 2>/dev/null)
ID=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# 2. Poll until complete
uv run {baseDir}/scripts/research.py status "$ID" 2>/dev/null

# 3. Save when done
uv run {baseDir}/scripts/research.py report "$ID" --output report.md
```

## Configuration Requirements

| Requirement | How to Check | How to Fix |
|-------------|-------------|------------|
| API key | `uv run {baseDir}/scripts/onboard.py --check` | `export GOOGLE_API_KEY='...'` |
| uv runtime | `which uv` | [uv install docs](https://docs.astral.sh/uv/getting-started/installation/) |

API key is checked from these env vars (first found wins):
1. `GEMINI_DEEP_RESEARCH_API_KEY`
2. `GOOGLE_API_KEY`
3. `GEMINI_API_KEY`

## Output Contracts

All scripts: **stderr** = human-readable (Rich), **stdout** = JSON.

### `research.py start` (non-blocking)

```json
{"id": "interaction-abc123", "status": "in_progress"}
```

### `research.py start --output-dir` (blocking)

```json
{
  "id": "interaction-abc123",
  "status": "completed",
  "output_dir": "output/research-interaction-a/",
  "report_file": "output/research-interaction-a/report.md",
  "report_size_bytes": 45000,
  "duration_seconds": 154,
  "estimated_cost_usd": 1.22,
  "summary": "First 200 chars..."
}
```

### `research.py start --dry-run`

```json
{
  "type": "cost_estimate",
  "disclaimer": "Estimates only. Actual costs depend on research complexity, search depth, and API pricing changes.",
  "currency": "USD",
  "estimates": {
    "context_upload": {
      "files": 42,
      "total_bytes": 523000,
      "estimated_tokens": 130750,
      "estimated_cost_usd": 0.02
    },
    "research_query": {
      "estimated_input_tokens": 325000,
      "estimated_output_tokens": 60000,
      "estimated_cost_usd": 1.37,
      "basis": "historical_average | default_estimate"
    },
    "total_estimated_cost_usd": 1.39
  }
}
```

### `research.py status`

```json
{"id": "interaction-abc123", "status": "completed", "outputCount": 5}
```

### `store.py create`

```json
{"name": "fileSearchStores/abc123", "displayName": "My Store"}
```

### `store.py query`

```json
{"store": "fileSearchStores/abc123", "query": "...", "response": "..."}
```

### `metadata.json` (in --output-dir)

```json
{
  "id": "interaction-abc123",
  "status": "completed",
  "report_file": "output/research-interaction-a/report.md",
  "report_size_bytes": 45000,
  "output_count": 5,
  "source_count": 15,
  "duration_seconds": 154,
  "usage": {
    "disclaimer": "Estimates based on output size and pricing heuristics. Actual billing may differ.",
    "output_bytes": 45000,
    "estimated_output_tokens": 11250,
    "estimated_input_tokens": 250000,
    "estimated_cost_usd": 1.22,
    "context_files_uploaded": 0,
    "context_bytes_uploaded": 0,
    "source_urls_found": 15
  }
}
```

## Error Handling

| Exit Code | Meaning | Recovery |
|-----------|---------|----------|
| 0 | Success | N/A |
| 1 | Error | Check stderr for details |

Common errors:
- **No API key**: Set env var, run `onboard.py --check` to verify
- **Timeout**: Increase `--timeout`, or use non-blocking mode and poll with `status`
- **Store not found**: Run `store.py list` to find valid store names
- **Upload rejected**: Check file size (<100 MB) and type (binary files are rejected)
- **API rate limit**: Wait and retry; the polling loop handles transient errors automatically

## Pricing Reference

These are heuristic estimates (Gemini API does not return token counts):

| Component | Rate | Notes |
|-----------|------|-------|
| Embeddings | $0.15 / 1M tokens | Context file uploads |
| Gemini Pro input | $2.00 / 1M tokens | Research query input |
| Gemini Pro output | $12.00 / 1M tokens | Research report output |
| Typical research | $1-3 per query | Varies with complexity |
| Context upload | $0.01-0.05 | Depends on file count/size |

Use `--dry-run` for per-query estimates.
