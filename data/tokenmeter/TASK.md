# TASK: Add API-based usage fetching with env var auto-detection

## Context
tokenmeter currently only imports from local session JSONL files. We need a `fetch` command that pulls usage from provider APIs using API keys found in environment variables.

## Requirements

### 1. Create `tokenmeter/fetcher.py`
A module that:
- Scans environment for known API key env vars
- Fetches usage data from provider APIs (where available)
- Stores results in the same SQLite database

**Known env vars to scan:**
- `ANTHROPIC_API_KEY` 
- `OPENAI_API_KEY` / `OPENAI_KEY`
- `GOOGLE_API_KEY` / `GEMINI_API_KEY`
- `AZURE_OPENAI_API_KEY`

**For Anthropic:** Use the messages API to check auth, but note there's no public usage API yet. Log a note that Anthropic doesn't expose a billing/usage endpoint — the local import method is the way to track Anthropic usage.

**For OpenAI:** Use `GET https://api.openai.com/v1/organization/usage/completions` with the API key. Parse the response and store records. If the API requires org-level access, handle gracefully with an error message.

**Implementation notes:**
- Use `requests` or `httpx` library (add to pyproject.toml dependencies)
- Dedup against existing records using the same import_log hash table
- Store with `source="fetch"` to distinguish from `source="import"` and `source="manual"`

### 2. Add CLI command in `cli.py`

```python
@app.command()
def fetch(
    provider: Optional[str] = typer.Argument(None, help="Provider to fetch (anthropic, openai, google). Omit for auto-detect."),
    scan: bool = typer.Option(True, "--scan/--no-scan", help="Auto-scan env vars"),
):
    """Fetch usage from provider APIs (auto-detects API keys in environment)."""
```

**Behavior:**
- No args: scan env vars, report what's found, fetch from all detected providers
- With provider arg: fetch from that specific provider only
- Show clear output: which keys found, what was fetched, any errors

**Example output:**
```
$ tokenmeter fetch
🔍 Scanning environment...
  ✅ ANTHROPIC_API_KEY found
  ✅ OPENAI_API_KEY found  
  ❌ GOOGLE_API_KEY not set

Fetching from OpenAI...
  ✅ 47 usage records imported ($12.34)

Note: Anthropic doesn't expose a usage API. Use 'tokenmeter import --auto' for local session data.

Fetching complete!
```

### 3. Add `requests` to dependencies in `pyproject.toml`

### 4. Clean up: Remove IMPLEMENTATION_PLAN.md from repo root (leftover from previous PR)

### 5. Commit and push to main

Commit message: `feat: add tokenmeter fetch command with env var auto-detection`

## Important
- Do NOT break existing import/dashboard/costs/summary commands
- Keep it simple — if a provider API isn't available, just print a helpful message
- Test that existing commands still work after changes
