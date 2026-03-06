# agentmail-to-inbox-ops

<p align="center">
  <a href="https://www.agentmail.to/" target="_blank" rel="noopener noreferrer">
    <img src="https://www.agentmail.to/favicon.ico" alt="Agentmail.to logo" width="72" height="72" />
  </a>
</p>

Openclaw skill for inbox workflows on top of **[agentmail.to](https://www.agentmail.to/)**.
This skill gives you clean, script-driven operations to read, filter, reply, process attachments, and keep inbox state in sync.

> Scope note: this skill is designed for **existing mailboxes** (`AGENTMAIL_INBOX`) and does **not** currently include inbox creation/provisioning commands.

## 60-second quick start

```bash
# 1) Go to the skill folder
cd skills/agentmail-to-inbox-ops

# 2) Install dependencies
uv sync

# 3) Create your env file
cp .env.example .env
# then edit .env with your real values

# 4) Run onboarding validator
uv run python scripts/check_onboarding.py

# 5) Run a safe first command (unread-only by default)
uv run python scripts/list_messages.py --limit 5
```

Expected: validator prints READY (or READY WITH WARNINGS), then list command prints JSON with `count` and `messages`.

## OpenClaw onboarding (required)

For OpenClaw to discover and onboard this skill correctly:

1. **Skill folder name must match `SKILL.md` frontmatter `name`**
   - required name: `agentmail-to-inbox-ops`
2. Place the folder in one of OpenClaw's skill roots:
   - `<workspace>/skills` (highest priority)
   - `~/.openclaw/skills`
3. Keep `SKILL.md` frontmatter metadata block (OpenClaw uses it for env/bin preflight checks).

Example install from this repo:

```bash
mkdir -p ~/.openclaw/skills/agentmail-to-inbox-ops
rsync -a --delete ./ ~/.openclaw/skills/agentmail-to-inbox-ops/
```

If your local folder is not named `agentmail-to-inbox-ops` (for example `agentmail-skill`), copy/sync it using the required target name above.

## Environment

Required:
- `AGENTMAIL_API_KEY`

Optional:
- `AGENTMAIL_INBOX` (default inbox)
- `AGENTMAIL_ALLOWED_SENDERS` (comma-separated sender allowlist for read/reply filtering)

See `.env.example`.

## Command cheat sheet

```bash
# List unread messages (default unread-only, token-thrifty)
uv run python scripts/list_messages.py --limit 10

# Include read messages explicitly
uv run python scripts/list_messages.py --include-read --limit 20

# Get one full message
uv run python scripts/get_message.py <message_id>

# Download attachments from a message (HTTPS only, filename/path sanitized)
uv run python scripts/download_attachments.py <message_id> --out-dir ./downloads

# Analyze local attachment metadata (safe default; PDF/DOCX text extraction disabled)
uv run python scripts/analyze_attachment.py ./downloads/file.docx

# Opt in to PDF/DOCX text extraction with limits/timeouts
uv run python scripts/analyze_attachment.py ./downloads/file.docx --extract-text --max-bytes 10485760 --parse-timeout-seconds 8

# Reply to allowlisted sender(s) from .env (dry run first)
uv run python scripts/reply_messages.py --text "Received." --dry-run

# Reply with explicit sender override
uv run python scripts/reply_messages.py --from-email sender@example.com --text "Received." --dry-run

# Real reply (default marks replied messages as read)
uv run python scripts/reply_messages.py --text "Received. Working on it."

# Keep unread instead
uv run python scripts/reply_messages.py --from-email sender@example.com --text "Received." --keep-unread

# Set explicit read/unread
uv run python scripts/set_read_state.py <message_id> read
uv run python scripts/set_read_state.py <message_id> unread

# Monitor unified logs
tail -f inbox_ops.log
```

## Safe defaults

- `list_messages.py` defaults to **unread-only** and `--limit 10`.
- `reply_messages.py` defaults to **unread-only** and `--limit 10`.
- `reply_messages.py` marks replied emails as read by default.
- Use `--dry-run` for preview before sending replies.
- `download_attachments.py` sanitizes attachment filenames, enforces output-dir containment, and downloads over HTTPS only.
- `analyze_attachment.py` treats attachments as untrusted input and skips PDF/DOCX parsing unless `--extract-text` is provided.
- `analyze_attachment.py` enforces file size, extraction length, and parser timeout limits.

## Attachment security notes

- Treat all attachments as untrusted input.
- Prefer analyzing attachments in a sandboxed/containerized environment when enabling `--extract-text`.
- PDF/DOCX parsing uses external libraries and runs in a subprocess with timeout/resource limits, but sandboxing is still recommended.
- Analyzer output includes `sha256`, `parse_skipped_reason`, and `parse_error` fields to support safer automation decisions.

## Quick smoke test (no outgoing email)

```bash
uv run python scripts/list_messages.py --limit 3
uv run python scripts/reply_messages.py --text "test" --dry-run --limit 3
```

## Troubleshooting

- `Missing AGENTMAIL_API_KEY`:
  - set it in `.env` or export env var in shell.
- `count: 0` from list:
  - no unread emails, wrong inbox, or wrong key.
  - try `--include-read` to validate access.
- Dependency/import errors:
  - run `uv sync` again.
  - run `uv run python -m unittest discover -s tests -v` to verify local hardening checks.

## Public repo safety

Never commit:
- `.env`
- `inbox_ops.log`
- `downloads/`
- `.venv/`

These are already in `.gitignore`.
