# MODEL_GROUND_TRUTH.md
<!-- Machine-readable model configuration ground truth for OpenClaw. -->
<!-- Snapshot: YYYY-MM-DDTHH:MM TZ | OpenClaw vX.X.X -->
<!-- Usage: After each upgrade, run /verify against this file. -->
<!-- Format: YAML code blocks for AI parsing, Markdown for human readability. -->
<!-- Instructions: Replace all placeholder values with your actual configuration. -->

## Config: System Default

```yaml
# Your primary model — the default for all interactive sessions
primary_model: anthropic/claude-sonnet-4-6    # CHANGE THIS

# Session management
heartbeat_interval: 30m
compaction_mode: safeguard                     # safeguard | aggressive | off
context_pruning: cache-ttl (1h)                # cache-ttl | token-budget | off
max_concurrent_sessions: 7
max_concurrent_subagents: 8
```

## Config: Registered Models

```yaml
# List every model registered in agents.defaults.models
# Include alias and any special params
models:
  - id: anthropic/claude-sonnet-4-6            # CHANGE: your models
    alias: sonnet
    cache_retention: short
  - id: google/gemini-3-flash-preview
    alias: flash
  # Add more models as needed...
```

## Config: Auth Profiles

```yaml
# From auth.profiles in openclaw.json
auth_profiles:
  - id: google:default
    provider: google
    mode: api_key
  # Add your auth profiles...
```

## Cron Jobs: Model Assignments

```yaml
# List ALL recurring (non-deleteAfterRun) cron jobs
# One-shot jobs are NOT tracked — they self-destruct
cron_jobs:
  # Format:
  # - id: <first 8 chars of job ID>
  #   name: <job name>
  #   model: <full model ID>
  #   session_target: isolated | main
  #   schedule: "<cron expression>"
  #   delivery_to: "<discord channel ID>"  # optional comment

  - id: example1
    name: My recurring job
    model: google/gemini-3-flash-preview
    session_target: isolated
    schedule: "0 * * * *"
    delivery_to: "123456789"  # my-channel
```

## Non-LLM Providers (Phase 2 Liveness)

```yaml
# Optional: declare non-LLM providers for API key liveness checks.
# Each entry MUST specify allowed_domain — credentials are ONLY sent to matching HTTPS hosts.
# If this section is omitted, non-LLM liveness checks are skipped.
non_llm_providers:
  # - name: Brave Search
  #   allowed_domain: "api.search.brave.com"
  #   test_endpoint: "https://api.search.brave.com/res/v1/web/search?q=test&count=1"
  #   env_var: BRAVE_API_KEY
  #   auth_header: "X-Subscription-Token"
  #
  # - name: Notion
  #   allowed_domain: "api.notion.com"
  #   test_endpoint: "https://api.notion.com/v1/users/me"
  #   env_var: NOTION_TOKEN
  #   auth_header: "Authorization: Bearer"
```

## Verification Checklist

```yaml
# These checks run after each upgrade
# Add or remove checks based on your setup
checks:
  - name: primary_model
    command: "gateway config.get → agents.defaults.model.primary"
    expected: "anthropic/claude-sonnet-4-6"    # CHANGE THIS

  - name: registered_model_count
    command: "gateway config.get → Object.keys(agents.defaults.models).length"
    expected: 7                                 # CHANGE THIS

  - name: heartbeat_interval
    command: "gateway config.get → agents.defaults.heartbeat.every"
    expected: "30m"

  - name: cron_recurring_enabled_count
    command: "cron list (enabled, exclude deleteAfterRun) → count"
    expected: 17                                # CHANGE THIS

  - name: no_opus_cron
    command: "cron list → filter model contains 'opus' → count"
    expected: 0
    note: "Expensive models should never run in recurring cron"

  - name: compaction_mode
    command: "gateway config.get → agents.defaults.compaction.mode"
    expected: "safeguard"

  - name: acp_default_agent
    command: "gateway config.get → acp.defaultAgent"
    expected: "codex"                           # CHANGE THIS

  # Add channel-specific checks:
  # - name: discord_streaming
  #   expected: "off"
  # - name: whatsapp_group_policy
  #   expected: "disabled"
```

## Verification Script

```yaml
verify:
  path: skills/ground-control/scripts/post-upgrade-verify.md
  purpose: "Post-upgrade 5-phase system verification"
  trigger: "After openclaw upgrade, or manual /verify"
  model: google/gemini-3-flash-preview
  cost: "~$0.005 per run"
```

## Model Cost Tier Reference

```yaml
# Define your cost tiers for budgeting and cron assignment
cost_tiers:
  - tier: cheap
    models: [google/gemini-3-flash-preview]
    use_for: "cron workers, heartbeat, routine scans"

  - tier: standard
    models: [anthropic/claude-sonnet-4-6]
    use_for: "interactive chat, content generation, complex cron"

  - tier: expensive
    models: [anthropic/claude-opus-4-6]
    use_for: "complex reasoning only — NEVER in recurring cron"
```
