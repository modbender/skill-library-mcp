# 🧠 OpenCortex

**Self-improving memory architecture for [OpenClaw](https://github.com/openclaw/openclaw) agents.**

Stop forgetting. Start compounding.

---

## The Problem

Out of the box, OpenClaw agents dump everything into a flat `MEMORY.md`. Context fills up, compaction loses information, and the agent forgets what it learned last week. It's like having a brilliant employee with amnesia who takes notes on napkins.

## The Solution

OpenCortex transforms your agent into one that **gets smarter every day** through:

- **Structured memory** — Purpose-specific files instead of one flat dump
- **Nightly distillation** — Daily work automatically distilled into permanent knowledge
- **Weekly synthesis** — Pattern detection across days catches recurring problems and unfinished threads
- **Enforced principles** — Habits that prevent knowledge loss (decision capture, tool documentation, sub-agent debriefs)
- **Write-ahead durability** — Agent writes decisions and preferences to memory before responding, so nothing is lost if the session ends or compacts mid-conversation
- **Encrypted vault** — AES-256 encrypted secret storage with system keyring support
- **Voice profiling** *(opt-in)* — Learns how your human communicates for authentic ghostwriting
- **Infrastructure collection** *(opt-in)* — Auto-routes infrastructure details from daily logs to INFRA.md
- **Safe git backup** *(opt-in)* — Automatic secret scrubbing in an isolated copy — workspace files are never modified

## Quick Start

**Prerequisites:** [OpenClaw](https://github.com/openclaw/openclaw) 2026.2.x+ and [ClawHub CLI](https://clawhub.com)

```bash
# From your OpenClaw workspace directory (e.g. ~/clawd)
clawhub install opencortex
bash skills/opencortex/scripts/install.sh

# Preview without changing anything:
bash skills/opencortex/scripts/install.sh --dry-run

# Verify everything is working (read-only):
bash skills/opencortex/scripts/verify.sh
```

**Important:** Run the installer from your workspace root, NOT from inside the skill folder.

The installer asks about optional features, creates files (won't overwrite existing ones), and registers cron jobs. It makes zero network calls.

After install, customize:
1. `SOUL.md` — personality and identity
2. `USER.md` — info about your human
3. `MEMORY.md` — principles and project index
4. `TOOLS.md` — tools and APIs as you discover them
5. `INFRA.md` — infrastructure reference
6. `.secrets-map` — secrets for git scrubbing (if using git backup)

### From Source

```bash
git clone https://github.com/JD2005L/opencortex.git
cd opencortex && bash scripts/install.sh
```

## Updating

```bash
clawhub install opencortex --force         # Download latest
bash skills/opencortex/scripts/install.sh  # Detects existing install, offers Update
```

The installer detects your existing version and offers: **1) Update** (recommended), **2) Full reinstall**, **3) Cancel.** It never overwrites files you've customized.

### What the updater does

| Content | Update method | User data safe? |
|---------|--------------|-----------------|
| Principles (P1-P8) | Hash comparison, asks before replacing | ✅ Asks y/N per principle |
| P0 (Custom Principles) | Never touched | ✅ Your custom principles are always safe |
| Helper scripts (verify, vault, metrics, git-backup) | Checksum comparison, auto-replaced | ✅ These aren't user-edited |
| Reference docs (distillation, weekly-synthesis, architecture) | Checksum comparison, auto-replaced | ✅ These aren't user-edited |
| Cron job messages | Always updated to latest template | ✅ Only the message text changes |
| Cron model overrides | Cleared on every update | ✅ Gateway uses its configured default |
| Cron deduplication | Detects and removes duplicate crons from prior bugs | ✅ Keeps the first, deletes extras |
| Extra principles (P9+) | Detects duplicates and orphans, offers remove/migrate to P0 | ✅ Asks per principle |
| MEMORY.md bloat | Warns if >5KB, flags non-standard sections | ✅ Suggests what to move |
| Missing cron jobs | Offers to recreate with timezone auto-detection | ✅ Asks before creating |
| MEMORY.md structure (## Identity, ## Memory Index) | Adds missing core sections | ✅ Existing sections untouched |
| MEMORY.md index (### Infrastructure through ### Daily Logs) | Adds all 8 missing sub-sections | ✅ Existing sections untouched |
| preferences.md | Created if missing | ✅ Existing file untouched |
| New directories (contacts, workflows) | Created if missing | ✅ |
| AGENTS.md | Merges: regenerates standard sections, preserves custom sections | ✅ Custom sections appended |
| BOOTSTRAP.md | Merges: regenerates standard sections, preserves custom sections | ✅ Custom sections appended |
| SOUL.md | Created if missing | ✅ Existing file untouched |
| USER.md | Created if missing | ✅ Existing file untouched |
| .gitignore | Adds missing sensitive entries (.vault/, .secrets-map, etc.) | ✅ Existing entries untouched |

---

## Architecture

```
SOUL.md          ← Identity & personality
AGENTS.md        ← Operating protocol & delegation rules
MEMORY.md        ← Principles + index (< 3KB, loaded every session)
TOOLS.md         ← Tool shed: APIs, scripts with abilities descriptions
INFRA.md         ← Infrastructure atlas: hosts, IPs, services
USER.md          ← Your human's preferences
BOOTSTRAP.md     ← Session startup checklist

memory/
  projects/      ← One file per project (distilled, not raw)
  contacts/      ← One file per person/org (role, context, preferences)
  workflows/     ← One file per workflow/pipeline (services, steps, issues)
  runbooks/      ← Step-by-step procedures (delegatable to sub-agents)
  preferences.md ← Cross-cutting user preferences by category
  archive/       ← Archived daily logs + weekly summaries
  YYYY-MM-DD.md  ← Today's working log (distilled nightly)
```

## Principles (P0–P8)

| # | Principle | What It Does | Enforcement |
|---|-----------|-------------|-------------|
| P0 | Custom Principles | Your own principles (P0-A, P0-B, etc.) | Never modified by updates |
| P1 | Delegate First | Model-agnostic sub-agent delegation (Light/Medium/Heavy) | Agent protocol |
| P2 | Write It Down | Write-ahead durability: save before responding | Agent protocol |
| P3 | Ask Before External | Confirm before public/destructive actions | Agent protocol |
| P4 | Tool Shed & Workflows | Document tools and workflows | Nightly audit scans for undocumented tools and workflows |
| P5 | Capture Decisions & Preferences | Record decisions and preferences | Nightly + weekly audit for uncaptured decisions and preferences |
| P6 | Sub-agent Debrief | Delegated work feeds back to daily log | Nightly audit recovers orphaned debriefs |
| P7 | Log Failures | Tag failures with root cause analysis | Nightly audit checks for missing root causes |
| P8 | Check the Shed First | Use documented tools before deferring to user | Nightly audit flags unnecessary deferrals |

## How It Compounds

```
Week 1:  Agent knows basics, asks lots of questions
Week 4:  Agent has project history, knows tools, follows decisions
Week 12: Agent has deep institutional knowledge, patterns, runbooks
Week 52: Agent knows more about your setup than you remember
```

---

## Security Model

### Threat Model Summary

OpenCortex is a **workspace-scoped memory skill**. It creates files, registers cron jobs that run as isolated OpenClaw agent sessions, and optionally manages an encrypted vault. The primary risk surface is:

1. **Autonomous cron jobs** that read/write workspace files without human interaction
2. **Optional features** that collect sensitive data (voice patterns, infrastructure details)
3. **Optional git backup** that handles secret scrubbing before commits

OpenCortex contains **zero network operations** — no telemetry, no phone-home, no external endpoints. Every script is plain bash. [Full source is public.](https://github.com/JD2005L/opencortex)

### Default State: What's On and Off

| Feature | Default | Opt-In Required | What It Accesses | How to Disable |
|---------|---------|----------------|-----------------|----------------|
| Structured memory files | ✅ ON | — | Creates markdown files in workspace | Delete unwanted files |
| Daily distillation cron | ✅ ON | — | Reads/writes `memory/`, `MEMORY.md`, `TOOLS.md`, `USER.md` | `openclaw cron delete <id>` |
| Weekly synthesis cron | ✅ ON | — | Reads `memory/archive/`, writes summaries + runbooks | `openclaw cron delete <id>` |
| Principle enforcement audits | ✅ ON | — | Part of distillation — audits within workspace | Remove audit sections from cron message |
| Encrypted vault | Asked at install | Choose "direct" mode to skip | `.vault/` directory, system keyring | Don't init vault; delete `.vault/` |
| Voice profiling | ❌ OFF | `OPENCORTEX_VOICE_PROFILE=1` | Reads workspace conversation logs → `memory/VOICE.md` | Unset env var; delete `memory/VOICE.md` |
| Infrastructure collection | ❌ OFF | `OPENCORTEX_INFRA_COLLECT=1` | Routes infra mentions from daily logs → `INFRA.md` | Unset env var |
| Git backup | ❌ OFF | Say "yes" at install | Commits workspace to git (local only by default) | Remove from crontab; delete scripts |
| Git push to remote | ❌ OFF | `--push` flag on each run | Pushes scrubbed commits to remote | Don't pass `--push` |
| Daily metrics tracking | ❌ OFF | Say "yes" at install | Read-only file counts → `memory/metrics.log` | Remove from crontab; delete `metrics.log` |
| Broad file scrubbing | ❌ OFF | `OPENCORTEX_SCRUB_ALL=1` | Scrubs all tracked files (not just known text types) | Unset env var |
| File-based vault passphrase | ❌ OFF | `OPENCORTEX_ALLOW_FILE_PASSPHRASE=1` | Stores passphrase at `.vault/.passphrase` | Unset env var; use system keyring |

### What Runs Autonomously

Two cron jobs, both running as **isolated OpenClaw agent sessions** scoped to the workspace:

| Job | Schedule | Reads | Writes | Network Access |
|-----|----------|-------|--------|----------------|
| Daily Distillation | Daily 3 AM (local) | `memory/*.md`, workspace `*.md` | `memory/projects/`, `memory/contacts/`, `memory/workflows/`, `memory/preferences.md`, `MEMORY.md`, `TOOLS.md`, `USER.md`, daily log audit outputs | **None** |
| Weekly Synthesis | Sunday 5 AM (local) | `memory/archive/*.md`, `memory/projects/*.md`, `memory/contacts/*.md`, `memory/workflows/*.md`, `memory/preferences.md` | `memory/archive/weekly-*.md`, project/contact/workflow/preference files, `memory/runbooks/` | **None** |

Both jobs:
- Use a shared lockfile (`/tmp/opencortex-distill.lock`) to prevent conflicts
- Contain **no** `rm`, system modifications, network calls, or external API access
- Reference **only** workspace-relative paths (`memory/`, `MEMORY.md`, `TOOLS.md`, etc.)
- Are fully inspectable: `openclaw cron list`
- Are fully removable: `openclaw cron delete <id>`

**How cron jobs work:** OpenCortex does not bundle standalone distillation scripts. Instead, the installer registers OpenClaw cron jobs (`openclaw cron add`) with detailed task instructions. At runtime, OpenClaw spawns an isolated agent session that follows those instructions to read, synthesize, and write workspace files. The LLM agent is the executor — it's far better at knowledge synthesis than any bash script could be. The cron job messages *are* the implementation, fully viewable and editable via `openclaw cron list` / `openclaw cron edit`.

**On workspace isolation:** The cron instructions themselves don't enforce sandboxing — that's the **OpenClaw platform's** responsibility. OpenClaw cron jobs run in isolated sessions scoped to the workspace directory by the runtime, the same way a Dockerfile doesn't implement kernel isolation — the container runtime does. OpenCortex's cron instructions contain no references to external filesystems, network calls, or system commands beyond `openclaw cron list` and `crontab -l` (for self-auditing cron health).

### Git Backup Security

Git backup (when enabled) uses an **isolated copy approach** — your workspace files are never modified during scrubbing:

1. All files to commit are copied to a temp directory
2. Secrets are scrubbed in the copy only (using `.secrets-map` replacements)
3. The scrubbed copy is verified — if any raw secrets remain, the backup aborts immediately
4. A git commit is built from the scrubbed copy using git plumbing (`hash-object`, `update-index`, `write-tree`, `commit-tree`)
5. The temp directory is cleaned up
6. Your original workspace files are **untouched throughout the entire process**

Additional safeguards:
- `.secrets-map` and `.vault/` are always gitignored (enforced at install)
- Pre-backup check aborts if either exists but isn't gitignored
- Push requires explicit `--push` flag — local-only by default
- `.secrets-map` has 600 permissions (owner-only read/write)

**Recommendation:** Test in a disposable repo first. Run the backup, inspect the commit diff, and confirm scrubbing works before pointing at a real remote.

### Vault Security

The encrypted vault stores secrets at rest via GPG symmetric encryption (AES-256). Passphrase storage uses the **best available backend** (auto-detected):

| Priority | Backend | Passphrase Location | On Disk? |
|----------|---------|-------------------|----------|
| 1 | secret-tool (Linux keyring) | GNOME/KDE keyring | No |
| 2 | macOS Keychain | Native macOS keystore | No |
| 3 | keyctl (Linux kernel keyring) | Kernel memory | No |
| 4 | Environment variable | `OPENCORTEX_VAULT_PASS` | No |
| 5 | File fallback | `.vault/.passphrase` (mode 600) | Yes — requires `OPENCORTEX_ALLOW_FILE_PASSPHRASE=1` |

Commands: `vault.sh init`, `vault.sh set <key> <value>`, `vault.sh get <key>`, `vault.sh rotate`, `vault.sh migrate`, `vault.sh backend`

Key names are validated on set (alphanumeric + underscores only).

### Install Mechanism

The installer (`scripts/install.sh`) is a single bash script that:
- Creates markdown files (only if they don't already exist)
- Creates directories (`memory/projects/`, `memory/contacts/`, `memory/workflows/`, `memory/runbooks/`, `memory/archive/`)
- Registers OpenClaw cron jobs via `openclaw cron add`
- Optionally copies bundled `git-backup.sh` and `vault.sh` scripts to the workspace

**No external downloads.** No package installs. No network calls. No binaries. All code is plain bash + markdown, bundled in the skill package and fully auditable.

### Credentials

OpenCortex declares **no required API keys or environment variables**. The cron jobs use your gateway's default model — OpenCortex never sees or handles model provider keys. Any model capable of reading and writing markdown files will work.

Optional environment variables (all off by default):

| Variable | Purpose | Sensitive |
|----------|---------|-----------|
| `CLAWD_WORKSPACE` | Override workspace directory (defaults to cwd) | No |
| `CLAWD_TZ` | Timezone for cron scheduling (defaults to UTC) | No |
| `OPENCORTEX_VAULT_PASS` | Vault passphrase via env var (prefer keyring) | Yes |
| `OPENCORTEX_VOICE_PROFILE` | Enable voice profiling in distillation | No |
| `OPENCORTEX_INFRA_COLLECT` | Enable infrastructure auto-collection | No |
| `OPENCORTEX_SCRUB_ALL` | Scrub all tracked files during git backup | No |
| `OPENCORTEX_ALLOW_FILE_PASSPHRASE` | Allow file-based vault passphrase | No |

---

## What to Review Before Installing

1. **Read the scripts.** They're bundled plain bash — `install.sh`, `update.sh`, `vault.sh`, `git-backup.sh`, `verify.sh`, `metrics.sh`. You can read every line before running anything. Required binaries: `grep`, `sed`, `find`. Optional: `git`, `gpg`, `openssl`, `openclaw`, `secret-tool`, `keyctl`, `file` (for binary detection during scrubbing).
2. **Confirm workspace isolation.** OpenCortex delegates sandbox enforcement to the OpenClaw platform. Verify your OpenClaw instance enforces workspace-only behavior for cron sessions. If isolation is misconfigured, a cron session could theoretically access files outside the workspace.
3. **Inspect cron messages after install.** Run `openclaw cron list` to see the exact instructions registered. These are the actual implementation — edit or remove them freely.
4. **Prefer system keyring for vault.** Use `secret-tool`, macOS Keychain, or `keyctl` over file-based passphrase storage. Set `OPENCORTEX_ALLOW_FILE_PASSPHRASE=1` only if no keyring is available and you accept the risk.
5. **Test git backup in a disposable repo.** Verify `.secrets-map` entries scrub correctly before using on a real remote.
6. **Opt-in features are off by default.** Voice profiling, infrastructure collection, broad scrubbing, and git push all require explicit activation. Only enable what you need.
7. **Consider disabling voice profiling** if you're uncomfortable with the agent building a persistent behavioral profile from conversations.

---

## Metrics & Growth Tracking

If enabled during install, OpenCortex tracks your agent's knowledge growth over time. A daily system cron (11:30 PM local) snapshots file counts, decision captures, tool documentation, and more into `memory/metrics.log`. No sensitive data is collected — only counts and pattern matches.

### What's Tracked

| Metric | What It Measures |
|--------|-----------------|
| Knowledge files | Total files in `memory/projects/`, `memory/contacts/`, `memory/workflows/`, `memory/runbooks/`, and `memory/` |
| Knowledge size (KB) | Total size of knowledge files |
| Decisions captured | `**Decision:**` entries across all memory files |
| Preferences captured | `**Preference:**` entries in `memory/preferences.md` |
| Contacts | People/orgs documented in `memory/contacts/` |
| Workflows | Pipelines/automations in `memory/workflows/` |
| Runbooks | Reusable procedures in `memory/runbooks/` |
| Tools documented | Entries in `TOOLS.md` |
| Failures logged | `❌ FAILURE:` and `🔧 CORRECTION:` entries |
| Debriefs | Sub-agent debrief entries in daily logs |
| Projects | Files in `memory/projects/` |
| Archive files | Distilled daily logs in `memory/archive/` |

### Commands

```bash
# Snapshot today's metrics
bash scripts/metrics.sh --collect

# Show trends with ASCII growth charts + compound score
bash scripts/metrics.sh --report

# Last 4 weeks only
bash scripts/metrics.sh --report --weeks 4

# JSON output (for integrations)
bash scripts/metrics.sh --json
```

Or just ask your agent: *"How is OpenCortex doing?"* or *"Show me OpenCortex metrics."*

### Compound Score

The report includes a 0–100 compound score reflecting knowledge depth, growth rate, and tracking consistency:

| Score | Rating |
|-------|--------|
| 80–100 | Thriving — deep knowledge, steady growth |
| 60–79 | Growing — good foundation, building momentum |
| 40–59 | Developing — basics in place, room to grow |
| 20–39 | Getting started — early days |
| 0–19 | Just installed — give it time |

A healthy OpenCortex installation trends upward over weeks. Flat or declining scores highlight specific areas to focus on.

### Weekly Summary

If metrics tracking is enabled, the weekly synthesis cron automatically includes a metrics report in its output — showing 4-week trends and flagging areas that need attention.

### Security

The metrics script (`scripts/metrics.sh`) is **read-only** — it only counts files and greps for patterns. It writes only to `memory/metrics.log` (append-only in `--collect` mode). No network access, no sensitive data captured (counts, never content), no system modifications.

---

## Customization

**Add a project:** Create `memory/projects/my-project.md`, add to MEMORY.md index. Nightly distillation routes relevant daily log entries to it.

**Add a contact:** Create `memory/contacts/name.md` with: name, role/relationship, context, communication preferences. Distillation auto-creates contacts mentioned in conversation.

**Add a workflow:** Create `memory/workflows/my-pipeline.md` with: what it does, services involved, how to operate it. Distillation auto-creates workflows when described.

**Add a preference:** Append to `memory/preferences.md` under the right category. Format: `**Preference:** [what] — [context] (date)`. Distillation auto-captures preferences stated in conversation.

**Add a principle:** Append to MEMORY.md under 🔴 PRINCIPLES. Keep it short.

**Add a runbook:** Create `memory/runbooks/my-procedure.md` with step-by-step instructions. Sub-agents follow these directly.

**Add a tool:** Add to TOOLS.md with: what it is, how to access it, goal-oriented abilities description.

**Change cron schedule:** `openclaw cron list` then `openclaw cron edit <id> --cron "..."`.

**Run fully air-gapped:** Decline all optional features during install. No voice profiling, no infrastructure collection, no git backup. The core memory architecture and distillation work entirely offline.

## Requirements

- [OpenClaw](https://github.com/openclaw/openclaw) 2026.2.x+
- **Required:** `grep`, `sed`, `find` (standard on most systems)
- **Optional:** `git` (for backup), `gpg` (for vault), `openssl` (for passphrase generation)

## License

MIT

## Credits

Created by [JD2005L](https://github.com/JD2005L)
