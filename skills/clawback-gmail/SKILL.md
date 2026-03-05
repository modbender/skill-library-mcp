---
name: clawback
description: Gmail security proxy with policy enforcement, approval workflows, and audit logging. Use when the user wants to read, search, or send Gmail with guardrails — send actions may require human approval before executing.
homepage: https://clawback.sh
metadata:
  {
    "openclaw":
      {
        "emoji": "🛡️",
        "requires": { "bins": ["clawback"] },
        "install": [],
      },
  }
---

# clawback

Use `clawback` for Gmail with policy enforcement. All operations go through a server-side proxy that enforces policies and logs an audit trail. Sends may require human approval.

Install (if not already installed)

```bash
curl -fsSL https://clawback.sh/install | bash
```

Setup (once)

- `clawback auth login` (device flow — opens browser)
- `clawback auth status` (verify connection)

Common commands

- Gmail search: `clawback gmail search 'newer_than:7d' --max 10`
- Gmail search (all pages): `clawback gmail search 'from:boss@company.com' --all --json`
- Gmail get message: `clawback gmail get <messageId> --json`
- Gmail send (plain): `clawback gmail send --to a@b.com --subject "Hi" --body "Hello"`
- Gmail send (multi-line): `clawback gmail send --to a@b.com --subject "Hi" --body-file ./message.txt`
- Gmail send (stdin): `clawback gmail send --to a@b.com --subject "Hi" --body-file -`
- Gmail send (HTML): `clawback gmail send --to a@b.com --subject "Hi" --body-html "<p>Hello</p>"`
- Gmail send (reply): `clawback gmail send --to a@b.com --subject "Re: Hi" --body "Reply" --reply-to-message-id <msgId> --thread-id <threadId>`
- Gmail send (attachment): `clawback gmail send --to a@b.com --subject "Report" --body "See attached" --attach ./report.pdf`
- Thread list: `clawback gmail thread list 'subject:meeting' --max 20`
- Thread get: `clawback gmail thread get <threadId> --json`
- Thread modify labels: `clawback gmail thread modify <threadId> --add STARRED --remove UNREAD`
- Labels list: `clawback gmail labels list`
- Labels create: `clawback gmail labels create --name "Important/Clients"`
- Labels modify message: `clawback gmail labels modify <messageId> --add STARRED --remove UNREAD`
- Drafts list: `clawback gmail drafts list --json`
- Drafts create: `clawback gmail drafts create --to a@b.com --subject "Draft" --body "WIP"`
- Drafts send: `clawback gmail drafts send <draftId>` (may trigger approval — exit code 8)
- Drafts delete: `clawback gmail drafts delete <draftId>`
- Download attachment: `clawback gmail attachment <messageId> <attachmentId> --out ./file.pdf`
- History: `clawback gmail history --since <historyId> --max 50`
- Batch delete: `clawback gmail batch delete <id1> <id2> <id3>`
- Batch modify: `clawback gmail batch modify <id1> <id2> --add INBOX --remove SPAM`
- Settings filters list: `clawback gmail settings filters list --json`
- Settings send-as list: `clawback gmail settings send-as list`
- Settings vacation get: `clawback gmail settings vacation get`
- Settings forwarding list: `clawback gmail settings forwarding list`
- Settings delegates list: `clawback gmail settings delegates list`
- Approvals list: `clawback approvals list --status pending --json`
- Approvals get: `clawback approvals get <approvalId> --json`
- Policy list: `clawback policy list --json`

Approval Flow

Sends may be intercepted by an `approve_before_send` policy. When this happens:

1. The send command exits with code **8** and prints the approval ID
2. Check status: `clawback approvals get <approvalId> --json`
3. A human must approve via the dashboard or email link
4. Once approved, the server sends the email automatically
5. If rejected or expired, inform the user

Exit Codes

- 0: success
- 1: unexpected error
- 3: no results (with `--fail-empty`)
- 4: not authenticated — run `clawback auth login`
- 6: blocked by policy (read_only) — inform user
- 8: pending approval — poll `clawback approvals get <id>` until resolved
- 130: cancelled

Notes

- Set `CB_SERVER=https://your-server.example.com` to override the default server.
- For scripting, prefer `--json` plus `--no-input` plus `--fail-empty`.
- `--connection <id>` selects which Gmail connection to use; auto-detected if you have one connection.
- `--all` auto-paginates search results (gmail search and thread list).
- `--select field1,field2` projects JSON output to specific fields.
- `--results-only` strips the envelope and returns just the data array.
- Confirm before sending mail. If exit code is 8, do not retry — wait for human approval.
