# SECURITY.md — Meeting Autopilot Security Model

## What Data This Skill Touches

| Data | Access | Notes |
|------|--------|-------|
| Meeting transcripts | **Read** | Parsed locally, then sent to LLM API for extraction |
| LLM API (Anthropic/OpenAI) | **Network** | Transcript content sent for item extraction and output generation |
| History files (`~/.meeting-autopilot/history/`) | **Write** | Extracted items stored locally as JSON |
| Report output | **Write** (optional) | Markdown report saved to user-specified directory |

## ⚠️ Data Sensitivity Warning

**Meeting transcripts often contain sensitive information** — strategy discussions, personnel matters, financial data, confidential projects. Be aware:

- Transcript content IS sent to the configured LLM API (Anthropic or OpenAI) for processing
- The LLM provider's data handling policies apply
- No data is sent to CacheForge or any other third party
- Consider your organization's data policies before processing sensitive meetings

## Input Validation

- **File paths:** Validated via `[ -f "$path" ]` before reading. No glob expansion of user input.
- **Transcript content:** Validated for minimum length. Passed to Python parsers via **stdin** (not string interpolation).
- **JSON construction:** All JSON is built via `jq -n --arg` / `jq --argjson` — never via string concatenation with user data.
- **Meeting titles:** Passed to scripts as quoted arguments and to `jq` via `--arg`.

## Security Patterns (What We Do / Don't Do)

### ✅ Safe Patterns Used
- All user-controlled strings passed via env vars or stdin to Python
- All JSON construction via `jq --arg` / `jq -n`
- Python parsers receive data via `sys.stdin.read()`, never via f-string or format injection
- LLM request bodies built entirely through `jq -n` with `--arg` for all variable content
- Temporary files created in system temp directory with `mktemp`
- Temp directory cleaned up via `trap ... EXIT`

### ❌ Patterns We Avoid
- No `eval` on any user-controlled data
- No backtick substitution on user-controlled data
- No `'''${VAR}'''` Python injection patterns
- No `echo "$user_data" | python3 -c "...f'{}'..."` patterns
- No string concatenation into JSON — always `jq --arg`
- No `source` of user-provided files

## Abuse Cases & Mitigations

| Abuse Case | Risk | Mitigation |
|------------|------|------------|
| Malicious transcript content triggers LLM injection | **Medium** | LLM prompts are structured with clear system/user separation. User content is clearly delineated as "TRANSCRIPT:" block. Cannot override system instructions in standard API usage. |
| Transcript with shell metacharacters in speaker names | **Low** | Speaker names extracted via Python JSON parsing, never executed in shell context. All values go through `jq --arg` for JSON output. |
| Path traversal via filename argument | **Low** | File existence checked via `[ -f "$path" ]`. History filenames are sanitized (alphanumeric + hyphens only). |
| Large transcript causes memory exhaustion | **Low** | Bounded by LLM context window. Extremely large files may cause Python to use significant memory but will not crash the system. |
| History directory symlink attack | **Low** | `mkdir -p` follows symlinks but creates the directory. History files are JSON only, never executed. |
| Sensitive meeting content in history files | **Medium** | History stores extracted items, not full transcripts. Users can delete history at `~/.meeting-autopilot/history/`. `--no-history` flag skips storage entirely. |

## Network Behavior

This skill makes API calls ONLY to the configured LLM provider:
- **Anthropic:** `https://api.anthropic.com/v1/messages` (or custom `ANTHROPIC_API_URL`)
- **OpenAI:** `https://api.openai.com/v1/chat/completions` (or custom `OPENAI_API_URL`)

No other network calls are made. No telemetry. No phone-home.

## What This Skill Does NOT Do

- Does not record or transcribe audio
- Does not access your calendar or email
- Does not send emails on your behalf (generates drafts only)
- Does not create tickets automatically (generates drafts only)
- Does not store full transcripts (only extracted items in history)
- Does not phone home or send telemetry
- Does not access any service beyond the configured LLM API
