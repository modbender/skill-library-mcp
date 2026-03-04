---
name: token-usage-tracker
description: Token usage logging, alerting, and context-compression utilities for OpenClaw. Use when you want to track per-call token usage, normalize timestamps, and reduce context sent to LLMs via summarization/compression.
---

# token-usage-tracker

Quick start

1. Configure defaults in `skill-config.json` (timezone, log_folder).
2. Install scripts (examples provided) into your workspace and wire the interceptor into your message pipeline.
3. Use `scripts/context_summarizer.py` before sending large contexts to reduce token usage.

What this skill provides

- Logging: `token_tracker.py` writes per-call token usage to a JSONL log. Includes timestamp normalization.
- Interceptor: `token_interceptor.py` example that normalizes timestamps and forwards sanitized messages to the tracker.
- Alerts: `token_alerts.py` example for threshold-based alerts (no external posting by default).
- Compression: `context_summarizer.py` produces short summaries to reduce token payloads.
- Utilities: migration and cleanup scripts (convert timestamps, dedupe log entries).

When to use

- Use this skill when you want transparent per-call token accounting, to keep token usage low, or to protect sensitive/verbose contexts by summarizing before sending to the model.

Files

- scripts/
  - token_interceptor.py — example interceptor (normalizes timestamps)
  - token_tracker.py — logging helper
  - token_alerts.py — alert examples
  - context_summarizer.py — compression helper
  - migrate_timestamps.py — migration utility
  - dedupe_log.py — dedupe utility
- references/
  - examples/systemd/ — example unit files (install manually)
- skill-config.json — configurable defaults
- README.md — usage and install notes

Configuration

See `skill-config.json` for defaults. The skill exposes:
- timezone: default UTC
- log_folder: default ./skills/logs (relative to OpenClaw workspace)
- compression settings: summary_target_tokens, max_context_tokens

Security and installation

- The scripts are examples and safe by default. They do not change system state or install services automatically.
- Example systemd/unit files are provided in `references/systemd/` — apply them manually after review.

License: MIT (adapt as you prefer)
