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
      },
  }
---

# clawback

Use `clawback` for Gmail with policy enforcement. All operations go through a server-side proxy that enforces policies and logs an audit trail. Sends may require human approval.

Prerequisites

The `clawback` binary must be installed and on your PATH. If it's missing, releases are available at https://github.com/honeybadge-labs/clawback/releases.

Setup (once)

- `clawback auth login` (device flow — opens browser)
- `clawback auth status` (verify connection)

Common commands

- Gmail search: `clawback gmail search 'newer_than:7d' --max 10`
- Gmail search (all pages): `clawback gmail search 'from:boss@company.com' --all --json`
- Gmail get message: `clawback gmail get <messageId> --json`
- Gmail send (plain): `clawback gmail send --to a@b.com --subject "Hi" --body "Hello"`
- Gmail send (HTML): `clawback gmail send --to a@b.com --subject "Hi" --body-html "<p>Hello</p>"`
- Gmail send (reply): `clawback gmail send --to a@b.com --subject "Re: Hi" --body "Reply" --reply-to-message-id <msgId> --thread-id <threadId>`
- Thread list: `clawback gmail thread list 'subject:meeting' --max 20`
- Thread get: `clawback gmail thread get <threadId> --json`
- Thread modify labels: `clawback gmail thread modify <threadId> --add STARRED --remove UNREAD`
- Labels list: `clawback gmail labels list`
- Labels create: `clawback gmail labels create --name "Important/Clients"`
- Labels modify message: `clawback gmail labels modify <messageId> --add STARRED --remove UNREAD`
- Drafts list: `clawback gmail drafts list --json`
- Drafts create: `clawback gmail drafts create --to a@b.com --subject "Draft" --body "WIP"`
- Drafts send: `clawback gmail drafts send <draftId>` (may require approval)
- Drafts delete: `clawback gmail drafts delete <draftId>`
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

Agent behavior

- Never expose approval IDs, exit codes, or CLI commands to the user. Those are internal plumbing.
- When composing email on the user's behalf, draft a natural subject and body — don't parrot their words verbatim. If they say "send a hello to Alex," write a friendly greeting, not `--subject "hello" --body "hello"`.
- Confirm with the user before sending. Show them the draft (to, subject, body) and ask if it looks good.

Handling approvals (exit code 8)

When a send command exits with code 8, it means the email needs human approval before it goes out.

1. Tell the user in plain language: "Sent! It needs approval in Clawback before it goes through — I'll keep an eye on it."
2. Poll `clawback approvals get <approvalId> --json` in the background every ~30s.
3. When resolved, proactively tell the user: "Approved and delivered" or "The approval was rejected/expired — the email was not sent."
4. Never ask the user to run commands or check approval status themselves.

Handling other errors

- Exit 4 (not authenticated): "You're not signed in — let me open the login flow." Then run `clawback auth login`.
- Exit 6 (blocked by policy): "Your org's policy doesn't allow this action." Explain what was blocked.
- Exit 3 (no results): Report naturally, e.g. "No emails matched that search."
- Exit 1 (unexpected error): Report the error and suggest retrying.

Notes

- `CB_SERVER` defaults to `https://clawback.sh`; set it to use a different server.
- Prefer `--json` plus `--no-input` plus `--fail-empty` for reliable output parsing.
- `--connection <id>` selects which Gmail connection to use; auto-detected if you have one connection.
- `--all` auto-paginates search results (gmail search and thread list).
- `--select field1,field2` projects JSON output to specific fields.
- `--results-only` strips the envelope and returns just the data array.
