# WorkCRM (OpenClaw Skill)

A lightweight, local-first CRM with an explicit confirmation gate.

Product constraints (locked):
- Writes happen only after explicit confirmation: reply `记` to confirm, `不记` to reject.
- Drafts are retained for auditability.

## Chat usage (recommended)

Use any of these to reliably trigger CRM behavior:
- `crm: ...`
- `记一下：...`
- `先出草稿：...`

Flow:
1) You send a message.
2) WorkCRM replies with a draft.
3) You reply `记` or `不记`.

Note: this alpha skill provides the core engine + storage. Chat routing glue depends on your OpenClaw agent config.

## Local CLI (for verification/dev)

### Generate a draft

```bash
python -m workcrm draft "crm: talked to Alice, follow up next week"
```

This prints a JSON payload including a human message + pending draft id.

## Storage

- Default DB path: `~/.openclaw/workcrm/workcrm.sqlite3`
- Override with env var: `WORKCRM_DB_PATH=/path/to/workcrm.sqlite3`
- Or pass `--db /path/to/workcrm.sqlite3` to the CLI.

## Implementation notes

- Deterministic ordering is enforced for lists.
- Schema migrations are applied automatically on first use.
