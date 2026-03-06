---
name: restic-home-backup
description: Design, implement, and operate encrypted restic backups for Linux home directories with systemd automation, retention policies, and restore validation. Use when a user asks to back up ~/, set up daily/weekly/monthly backup jobs, harden backup security, or troubleshoot restore/integrity issues.
---

# Restic Home Backup

Define and deliver a production-ready restic backup setup for `~/` with encryption, deduplication, automated scheduling, and restore testing.

## Skill contract

- **Name:** `restic-home-backup`
- **Problem solved:** Provide reliable, encrypted, versioned backups of a Linux home directory with operational safety and repeatable recovery.
- **Inputs:**
  - Backup target type (`local disk`, `sftp`, `s3`, `b2`, etc.)
  - Repository endpoint/path
  - Secret handling method (env file or password file)
  - Schedule preferences (daily backup, weekly prune, monthly check)
  - Exclude patterns
- **Outputs:**
  - Installed and initialized restic repository
  - Backup/prune/check scripts
  - systemd service/timer units
  - Validation evidence (snapshots + test restore)
  - Short operator runbook
- **Safety boundaries (must never violate):**
  - Never print secrets or tokens in chat/log output.
  - Never delete snapshots/repositories without explicit user confirmation.
  - Never weaken permissions on credential files (`chmod 600` minimum).
  - Never claim backup success without checking command exit status and snapshot listing.
  - Never apply system changes implicitly: require explicit `--apply` (or explicit user confirmation) before writing to `/etc`, `/usr/local/bin`, or `/etc/systemd/system`.

## Workflow

### 1) Assess and confirm backup contract

Collect the minimum required values before changes:
- Source path (default `/home/<user>`)
- Destination repo and transport
- Retention policy (for example: `7d/4w/12m`)
- Preferred schedule in local timezone

If any critical value is missing, ask targeted questions.

### 2) Scaffold backup implementation

Use these resources:
- `scripts/bootstrap_restic_home.sh` to generate deterministic setup artifacts. It is PLAN-ONLY by default and requires explicit `--apply` for system changes. Optional flags control timer enablement, repository initialization, and initial backup run.
- `references/ops-checklist.md` for day-2 operations and troubleshooting.

Create:
- `/etc/restic-home.env` (root-readable only)
- `/usr/local/bin/restic-home-backup.sh`
- `/usr/local/bin/restic-home-prune.sh`
- `/usr/local/bin/restic-home-check.sh`
- `restic-home-backup.service/.timer`
- `restic-home-prune.service/.timer`
- `restic-home-check.service/.timer`

### 3) Harden and validate

Run and verify:
1. `restic snapshots`
2. One immediate backup run
3. One restore smoke test to temporary directory
4. `restic check` (or scheduled monthly deep check)

Validate failure behavior:
- Wrong password
- Unreachable repository
- Permission denied on env file

Report exact failing command + short corrective action.

### 4) Package and publish via ClawHub CLI (when requested)

When user requests publication:
1. Validate skill quality and structure.
2. Package skill.
3. Publish with `clawhub` CLI.
4. Verify install from registry in a clean environment.

Keep publish actions explicit and auditable.

## Response style requirements

Use descriptive language with concrete operational detail:
- Name the exact file path, service name, and command.
- State what changed and how to verify it.
- End multi-step tasks with explicit completion status.
