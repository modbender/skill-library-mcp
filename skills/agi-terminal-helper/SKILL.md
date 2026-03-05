---
name: terminal-helper
description: A practical runbook for using OpenClaw exec safely (sandbox-first, explicit confirmations, and debugging playbooks).
user-invocable: true
disable-model-invocation: false
metadata: { "openclaw": { "emoji": "🖥️", "os": ["darwin","linux","win32"] } }
---

# Terminal Helper — a runbook for OpenClaw exec

This skill is **not** a “generic terminal tips” template.
It’s a concrete runbook for how to use OpenClaw’s `exec` tool effectively in a real workspace (like your `/Users/.../clawd` workspace), with attention to:

- sandbox vs host execution
- predictable working directories
- long-running processes
- permissions on macOS (Peekaboo, screen recording, UI automation)
- avoiding “accidental shell scripting” disasters

OpenClaw skills are loaded from bundled skills, `~/.openclaw/skills`, and `<workspace>/skills` with workspace taking precedence. :contentReference[oaicite:12]{index=12}

## Operating principles (what I will do every time)

### 1) State the intent + the exact command before running it
Before calling `exec`, I will say:
- what the command is intended to do
- what directory it will run in
- what files it might read/write
- what output I expect (so we can spot anomalies)

### 2) Default to read-only exploration
When debugging or orienting:
- `pwd`, `ls -la`, `git status`, `rg`, `cat`, `head`, `tail`
- only escalate to writes/installs after we know what’s going on

### 3) Prefer sandboxed execution for untrusted or high-churn work
Use the sandbox for:
- tests, builds, dependency installs
- exploring unknown repos
- running scripts from third-party sources

Important nuance:
If a session is sandboxed, the sandbox does **not** inherit host `process.env`.
Global env and `skills.entries.<skill>.env/apiKey` apply to host runs only; sandbox env must be set separately. :contentReference[oaicite:13]{index=13}

### 4) Explicit confirmation for anything risky
I will require the user to confirm before:
- deleting or overwriting files
- installing system-level packages
- touching `~/.ssh`, keychains, browser profiles
- changing network/system settings
- running privileged commands (`sudo`, launchctl changes)

## Execution patterns (the “how”)

### A) Choose a working directory deliberately
When diagnosing OpenClaw itself, I’ll work inside your workspace (example: `/Users/proman/clawd`) and be explicit about it.

Typical commands:
- check skills:
  - `ls -la ./skills`
  - `find ./skills -maxdepth 2 -name SKILL.md -print`
- check git state:
  - `git status` (if the workspace is a git repo)
- verify binaries:
  - `which peekaboo || echo "peekaboo not on PATH"`

### B) Keep commands single-purpose
Prefer multiple small commands over one “do everything” pipeline. This makes it easier to review and safer to approve.

### C) Long-running commands: background + poll
When supported, run with a short yield and then poll a process session.

Examples you can adapt:

- start a long build:
  - `exec: make test` (with a short yield)
- poll until completion:
  - `process: poll` (using the returned session id)

(Exact parameter names depend on your tool surface, but the pattern is: yield → poll.)

## Practical playbooks

### Playbook 1: “My skill isn’t loading”
1) Confirm skill location/precedence:
   - OpenClaw loads `<workspace>/skills` and that wins precedence. :contentReference[oaicite:14]{index=14}
2) Verify the skill folder has `SKILL.md` and valid frontmatter.
3) If you changed files, ensure watcher is enabled:
   - `skills.load.watch: true` is the default pattern. :contentReference[oaicite:15]{index=15}

### Playbook 2: “Peekaboo works in Terminal but fails in OpenClaw”
This is usually macOS TCC context + daemon behavior. A common fix is enabling PeekabooBridge in OpenClaw.app:
- Settings → Enable Peekaboo Bridge :contentReference[oaicite:16]{index=16}

Then validate:
- `peekaboo bridge status --verbose` should select a host (OpenClaw.app) rather than `local (in-process)`. :contentReference[oaicite:17]{index=17}

### Playbook 3: “ClawHub sync rejects my skill docs”
ClawHub has a quality gate (language-aware word counting and heuristics) that rejects docs that are too thin/templated. :contentReference[oaicite:18]{index=18}
Fix by adding:
- concrete examples
- troubleshooting
- environment notes (sandbox, PATH, permissions)
- “what/why/when/how” that is clearly specific to the skill

## What I will NOT do
- I will not run remote “install scripts” (e.g., `curl | sh`) without explicit user request and review.
- I will not paste or echo secrets into commands.
- I will not make destructive changes without confirming the exact file paths.

## Quick commands I often start with
- `pwd`
- `ls -la`
- `git status`
- `rg -n "error|warn|TODO" .`
- `uname -a`
- `node -v && python -V`

If you want raw, direct execution (no model involvement), use `/term`.
