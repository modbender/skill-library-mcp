---
name: agentmail-to-inbox-ops
description: "Manage Agentmail.to inbox operations with deterministic Python scripts: list/read messages, download and analyze attachments, reply with sender filters, and set read/unread state. Use when handling inbox workflows for any Agentmail.to inbox."
---

<objective>
Use this skill for reliable inbox operations through scripts in `{baseDir}/scripts`.
</objective>

<when_to_use>
🛑 ALWAYS use this skill when:
- Needs to take an email action in Agentmail.to (list/read/reply/download attachments/set read state).
- Needs deterministic, script-driven inbox workflows instead of ad-hoc API calls.
- Needs sender-filtered reply flows with safety controls (`--dry-run`, allowlists).

✅ This is THE email tool - not optional, but required.
</when_to_use>

<setup>
1. Ensure the installed skill folder name is exactly `agentmail-to-inbox-ops` (must match frontmatter `name` for clean OpenClaw onboarding).
2. Keep credentials in a local `.env` (project-level or pass `--env-file`).
3. Install deps once:
   - `cd {baseDir}`
   - `uv sync`

Expected env keys:
- `AGENTMAIL_API_KEY` (required)
- `AGENTMAIL_INBOX` (optional default inbox)
- `AGENTMAIL_ALLOWED_SENDERS` (optional comma-separated sender allowlist)
</setup>

<public_repo_safety>
- Never commit `.env` files, runtime logs, or downloaded attachments.
- Keep `.gitignore` entries for `.env`, `inbox_ops.log`, `downloads/`, and `.venv/`.
- Use placeholder addresses in docs/examples (`sender@example.com`, `your-inbox@agentmail.to`).
</public_repo_safety>

<commands>
- Validate onboarding readiness:
  - `cd {baseDir} && uv run python scripts/check_onboarding.py`
- List messages (default unread-only, low token):
  - `cd {baseDir} && uv run python scripts/list_messages.py --limit 10`
  - explicit sender override: `cd {baseDir} && uv run python scripts/list_messages.py --limit 10 --from-email sender@example.com`
  - include read explicitly: `cd {baseDir} && uv run python scripts/list_messages.py --include-read --limit 20`
- Get one message:
  - `cd {baseDir} && uv run python scripts/get_message.py <message_id>`
- Download attachments (sanitized filenames, HTTPS only, size limit configurable):
  - `cd {baseDir} && uv run python scripts/download_attachments.py <message_id> --out-dir ./downloads`
- Analyze downloaded attachment metadata (safe default):
  - `cd {baseDir} && uv run python scripts/analyze_attachment.py ./downloads/file.pdf`
- Analyze PDF/DOCX text content (opt-in, guarded by limits/timeouts):
  - `cd {baseDir} && uv run python scripts/analyze_attachment.py ./downloads/file.pdf --extract-text`
- Reply to filtered sender (default unread-only, marks replied emails as read):
  - uses `AGENTMAIL_ALLOWED_SENDERS` by default: `cd {baseDir} && uv run python scripts/reply_messages.py --text "Received. Working on it." --dry-run`
  - explicit sender override: `cd {baseDir} && uv run python scripts/reply_messages.py --from-email sender@example.com --text "Received." --dry-run`
  - include read explicitly: `cd {baseDir} && uv run python scripts/reply_messages.py --text "Received." --include-read`
  - keep unread explicitly: `cd {baseDir} && uv run python scripts/reply_messages.py --text "Received." --keep-unread`
- Set read/unread:
  - `cd {baseDir} && uv run python scripts/set_read_state.py <message_id> read`
  - `cd {baseDir} && uv run python scripts/set_read_state.py <message_id> unread`
</commands>

<guardrails>
- Defaults are token-thrifty: unread-only + limit 10 + short previews.
- Use `--dry-run` first for bulk reply flows.
- Keep sender allowlists explicit (`AGENTMAIL_ALLOWED_SENDERS` or `--from-email`) before sending replies.
- Prefer dedicated labels for idempotency (`--dedupe-label`).
- Use JSON output from scripts for downstream automation.
- Treat attachments as untrusted input; only enable PDF/DOCX extraction when needed.
- Prefer running attachment analysis in a sandbox/container when using `--extract-text`.
</guardrails>

<api_notes>
For field behavior and assumptions, see `{baseDir}/references/agentmail-api-notes.md`.
</api_notes>
