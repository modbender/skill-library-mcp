# Post-Upgrade Verification — Agent Instructions

<!-- Execution prompt for post-upgrade verification. -->
<!-- Source of truth: MODEL_GROUND_TRUTH.md in workspace root -->
<!-- Trigger: after openclaw upgrade, or manual /verify command -->

You are the OpenClaw post-upgrade verification system. Execute all 5 Phases sequentially, then send a summary report.

## Principle

**OpenClaw maintains itself. We only verify the result matches ground truth.**
- Use OpenClaw native tools (gateway, cron, sessions_spawn, message) for all checks
- Never bypass OpenClaw to test things it manages
- Auto-fix config and cron drift; report-only for API keys and channels

## Auto-Fix Safety

This skill can modify runtime configuration (Phase 1: `gateway config.patch`) and cron jobs (Phase 3: `cron update`). These are powerful operations.

**Dry-run mode:** When invoked with `--dry-run` or when the user says "verify only" / "check only", skip all auto-fix actions and report drift as ❌ instead of ⚠️ AUTO-FIXED. Default is auto-fix enabled.

**Guard rails:**
- Auto-fix ONLY applies corrections toward GROUND_TRUTH — never invents values
- Each fix is logged with before/after values in the summary report
- If more than 3 fields need fixing in a single phase, pause and ask for human confirmation before proceeding
- Phase 2 (keys) and Phase 5 (channels) are NEVER auto-fixed

## Preparation

1. Read `MODEL_GROUND_TRUTH.md` from workspace root — parse all expected values
2. Use `session_status` to get current version and timestamp
3. Initialize results tracker for all 5 phases

## Phase 1: Config Integrity

Use `gateway config.get` to fetch the full config. Compare each field against GROUND_TRUTH:

Check list (adapt to your GROUND_TRUTH `checks` section):
- `agents.defaults.model.primary`
- `agents.defaults.models` count
- `agents.defaults.compaction.mode`
- `agents.defaults.contextPruning`
- `agents.defaults.heartbeat.every`
- `acp.defaultAgent`
- `acp.allowedAgents` (exact array match)
- Any channel-specific checks from your GROUND_TRUTH

For each field:
- ✅ Match → pass
- ❌ Mismatch → record `{ field, expected, actual }` and **auto-fix** via `gateway config.patch`, mark as `⚠️ AUTO-FIXED`

## Phase 2: API Key & Provider Liveness

**Test LLM providers through OpenClaw's routing layer:**

For each LLM provider in your registered models, spawn a minimal session:
```yaml
sessions_spawn:
  task: "Reply with exactly: KEY_OK"
  mode: run
  model: <provider/model-id>
  runTimeoutSeconds: 30
```

**Test non-LLM providers (Brave, Notion, etc.):**

Only test providers explicitly listed in your `MODEL_GROUND_TRUTH.md` under `non_llm_providers`. Each entry must declare its test endpoint AND its allowed domain. Do NOT scan environment variables or test arbitrary endpoints.

```yaml
# Example GROUND_TRUTH entry:
non_llm_providers:
  - name: Brave Search
    allowed_domain: "api.search.brave.com"
    test_endpoint: "https://api.search.brave.com/res/v1/web/search?q=test&count=1"
    env_var: BRAVE_API_KEY
    auth_header: "X-Subscription-Token"
  - name: Notion
    allowed_domain: "api.notion.com"
    test_endpoint: "https://api.notion.com/v1/users/me"
    env_var: NOTION_TOKEN
    auth_header: "Authorization: Bearer"
```

**Endpoint validation (MANDATORY before every curl):**
1. Parse the hostname from `test_endpoint`
2. Verify it matches `allowed_domain` exactly (no subdomain wildcards)
3. Verify the scheme is `https://` (never `http://`)
4. If validation fails → skip this provider, report ❌ ENDPOINT_REJECTED

```bash
# Validation pseudocode — agent MUST perform this check:
ENDPOINT_HOST=$(python3 -c "from urllib.parse import urlparse; print(urlparse('$TEST_ENDPOINT').hostname)")
if [ "$ENDPOINT_HOST" != "$ALLOWED_DOMAIN" ]; then
  echo "❌ ENDPOINT_REJECTED: $ENDPOINT_HOST does not match allowed_domain $ALLOWED_DOMAIN"
  # DO NOT send the curl request
fi
```

For each validated provider:
```bash
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 -m 15 \
  -H "<auth_header>: <value of env_var>" "<test_endpoint>"
```

**Scope restrictions:**
- Only env vars explicitly named in `non_llm_providers[].env_var` may be accessed — never enumerate or dump environment variables
- Only HTTPS endpoints whose hostname matches `allowed_domain` receive credentials
- Credentials are sent as headers only — never in URL query params or POST body
- If GROUND_TRUTH has no `non_llm_providers` section, skip Phase 2 non-LLM checks entirely

Judgment:
- Response received / HTTP 200 → ✅
- Auth error (401/403) → ❌ KEY_INVALID
- Rate limited (429) → ⚠️ RATE_LIMITED (not a key issue)
- Timeout → ❌ UNREACHABLE

**Do NOT auto-fix** — key issues need human intervention.

## Phase 3: Cron Integrity

Use `cron list` (include disabled) to get all jobs. Compare against GROUND_TRUTH `cron_jobs`.

**Only verify recurring jobs** — skip `deleteAfterRun` one-shot jobs.

For each GROUND_TRUTH recurring job:
1. Match by ID prefix
2. Check: `enabled`, `model`, `schedule`, `delivery.to`
3. Mismatch → **auto-fix** via `cron update`, mark as `⚠️ AUTO-FIXED`

Extra checks:
- Count by model tier (flash/sonnet) matches expected
- Zero expensive-tier models in recurring cron (hard rule)
- Unknown new jobs (not in GROUND_TRUTH) → ⚠️ report but don't delete

## Phase 4: Session Smoke Test

```yaml
sessions_spawn:
  task: "Reply with exactly: VERIFY_OK"
  mode: run
  model: <cheapest registered model>
  runTimeoutSeconds: 30
```

- Received "VERIFY_OK" → ✅
- Timeout or error → ❌ SESSION_BROKEN

## Phase 5: Channel Liveness

For each enabled channel, send a test message:

**Discord** (or any same-context channel):
```yaml
message:
  action: send
  channel: discord
  target: "<your ops channel>"
  message: "🔍 Post-upgrade channel liveness test — ignore this message."
```

**Cross-context channels** (e.g., WhatsApp from Discord session):
Must use `sessions_spawn` to test from an isolated session:
```yaml
sessions_spawn:
  task: "Send a message via <channel> to <target>: '🔍 Post-upgrade channel test'. Reply CHANNEL_OK if sent, or the error."
  mode: run
  model: <cheapest model>
  runTimeoutSeconds: 30
```

## Summary Report

Send to your ops channel:

```
🔍 **Post-Upgrade Verification Report**
📦 Version: vX.X.X
⏱️ YYYY-MM-DD HH:MM TZ

**Phase 1: Config Integrity** [✅/⚠️/❌] X/Y checks
  [list any drift + fix status]

**Phase 2: Provider Liveness** [✅/❌] X/Y providers
  [per-provider status]

**Phase 3: Cron Integrity** [✅/⚠️/❌] X/Y recurring jobs
  [list any drift + fix status]

**Phase 4: Session Smoke Test** ✅/❌

**Phase 5: Channel Liveness** ✅/❌
  [per-channel status]

**Overall: ✅ PASS / ⚠️ DEGRADED (auto-fixed) / ❌ FAIL (needs human)**
```

If any ❌ FAIL → append: `🚨 Human intervention required`

Also write results to `memory/YYYY-MM-DD.md`.

## Rules

- Each Phase is independent — one failure does not block the next
- Auto-fix: Phase 1 (config) + Phase 3 (cron) only
- Report-only: Phase 2 (keys) + Phase 5 (channels)
- All curl commands use `--connect-timeout 10 -m 15`
