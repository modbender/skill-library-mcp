# workspace-standard

A structured, portable workspace standard for [OpenClaw](https://github.com/openclaw/openclaw) — directory layout, role-based file taxonomy, memory budgets, and maintenance tooling.

**Stop your AI agent from turning your workspace into a junk drawer.**

Organises your workspace into projects, roles, and runbooks. Budgets your memory file. Audits for staleness. Ships scripts that bootstrap and health-check. Zero dependencies.

[![ClawHub](https://img.shields.io/badge/ClawHub-workspace--standard-blue)](https://clawhub.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## ⚠️ Safety First

**This skill does not delete anything.** Nothing is removed, overwritten, or destroyed.

- `workspace-init.sh` **only creates** — new directories, new template files. If a file already exists, it's skipped (unless you pass `--force`).
- `workspace-audit.sh` **only reads** — it scans and reports. It changes nothing.
- Migration is **always manual** — you move the files yourself (or tell your agent to). Nothing is moved automatically.
- If your workspace is git-tracked, **every change is reversible** with `git checkout` or `git revert`.

### How to Undo Everything

If you bootstrap and don't like it:

```bash
# See what was added
git status

# Undo everything (if you haven't committed yet)
git checkout -- .
git clean -fd

# Undo after committing
git revert HEAD
```

If you migrated files and want to put them back:

```bash
# See the full history of moves
git log --stat

# Revert the migration commit
git revert <commit-hash>

# Or manually move files back
git mv projects/my-app/references/services.md docs/services.md
```

**No git?** The init script only creates new files and directories. Delete the new directories (`projects/`, `runbooks/`) and you're back where you started. Your original files are untouched.

---

## Why Would I Use This?

**Short answer:** Your agent writes dozens of files over days and weeks. Without structure, you end up with a flat pile of documents where nobody — not you, not the agent — can find anything or tell what's current and what's stale. This skill fixes that.

**What it does for you:**

- **Stops MEMORY.md from bloating.** Your agent loads MEMORY.md every session. If it's 300 lines of old context, you're wasting tokens and degrading reasoning quality. This skill enforces a 100-line budget and gives your agent clear rules for where else to put things.

- **Gives your agent a filing system.** Instead of dumping everything into `docs/`, every file gets a *role* — reference, plan, research, report, runbook, log, or entity. The agent knows where to write without you telling it every time.

- **Makes files self-describing.** YAML front-matter on every file means you (and your agent, and the audit script) can tell what a file is, when it was last updated, and whether it's gone stale — without reading it.

- **Separates your projects.** Each project gets its own directory. You can add a new project in 5 seconds without affecting anything else. You can archive or remove a project without cleaning up scattered references.

- **Gives you an audit tool.** One command tells you: is your MEMORY.md over budget? Which files are stale? Which projects are missing documentation? Which files don't have front-matter? Exit code zero means your workspace is clean.

- **Works from day one and day one hundred.** Whether you're starting fresh or you've been running an agent for months, the init script bootstraps the structure and the audit tells you what needs attention.

**What it doesn't do:**

- It doesn't touch your existing files unless you explicitly move them
- It doesn't require any API keys, databases, or external services
- It doesn't lock you in — remove the skill and your files are still plain markdown in directories

> **Ask your agent:** *"Why would I use the workspace-standard skill? What would it change about how you organise my files?"* — it'll give you a personalised answer based on your current workspace state.

---

## The Problem

If you run an AI agent long enough, this happens:

```
workspace/
├── MEMORY.md          ← 300 lines, half of it stale
├── docs/
│   ├── api-plan.md
│   ├── old-notes.md
│   ├── deploy-v2.md
│   ├── research.md
│   ├── audit.md
│   ├── infra.md       ← is this current? who knows
│   ├── misc.md
│   └── ... 40 more files, no structure
└── memory/
    └── ... write-only daily logs nobody reads
```

No project boundaries. No way to tell a plan from a reference from an audit. MEMORY.md bloats because there's nowhere else to put state. The agent writes the right information to the wrong place. Every session wastes tokens loading stale context.

## The Solution

This skill gives your agent — and you — a clear structure:

```
workspace/
├── MEMORY.md                # Current state (≤100 lines, strictly budgeted)
│
├── projects/                # Each project is self-contained
│   ├── _index.md            # Project registry
│   └── my-project/
│       ├── README.md        # Overview + current state
│       ├── references/      # Facts about how things ARE (→ kept current)
│       ├── plans/           # How you INTEND to do things (→ active or completed)
│       ├── research/        # What you INVESTIGATED (→ write-once)
│       └── reports/         # What you ASSESSED at a point in time (→ snapshots)
│
├── runbooks/                # Cross-project operational knowledge
│   ├── policies.md          # Governance rules
│   └── lessons-learned.md   # Debugging knowledge (append-only)
│
├── memory/                  # Episodic memory
│   ├── 2026-02-19.md        # Daily logs (write-once, never edited)
│   └── entities/            # People, servers, decisions
│
└── skills/                  # Procedural memory
```

Every file gets a **role** (via YAML front-matter) that determines where it lives, how it ages, and when it gets flagged as stale. The agent knows exactly where to write things without being told.

## What's in the Box

| File | What it does |
|------|-------------|
| `SKILL.md` | The standard — directory layout, role taxonomy, where-to-write rules, front-matter spec, memory budget, configuration, migration guide |
| `scripts/workspace-init.sh` | Bootstrap a new workspace or add a project. Creates directories, seeds templates with front-matter, registers projects. |
| `scripts/workspace-audit.sh` | Audit workspace health — root files, memory budget, project structure, front-matter coverage, staleness detection. Exit code = issue count. |
| `references/roles-guide.md` | Detailed guide to the 7 roles: what each means, examples, how it ages, how the audit treats it, and a "the test" question to resolve ambiguity |
| `references/maintenance-checklist.md` | Weekly maintenance procedure with checkboxes and time estimates |

## The Seven Roles

Every file gets one role. The role is its job title.

| Role | What it means | Where it lives | How it ages |
|------|--------------|----------------|-------------|
| **reference** | Facts about how things are *right now* | `projects/*/references/` | Must be kept current — stale references are lies |
| **plan** | How you intend to do something | `projects/*/plans/` | Active → completed or stale |
| **research** | What you investigated | `projects/*/research/` | Write-once — a record of thinking |
| **report** | What you assessed at a point in time | `projects/*/reports/` | Snapshot — never edited, superseded by new reports |
| **runbook** | How to do something (procedure) | `runbooks/` | Must be kept current — outdated runbooks are dangerous |
| **log** | What happened | `memory/YYYY-MM-DD.md` | Write-once, never edited — the audit trail |
| **entity** | Structured facts about a thing | `memory/entities/` | Updated when the thing changes |

**Quick decision tree:** Is it about how things are? → `reference`. How to change them? → `plan`. Comparing options? → `research`. A snapshot assessment? → `report`. A reusable procedure? → `runbook`. What happened today? → `log`. A specific person/server/decision? → `entity`.

See [`references/roles-guide.md`](references/roles-guide.md) for the full explanation with examples and tests for each role.

## Getting Started

### Option 1: Install via ClawHub (recommended)

```bash
clawhub install workspace-standard
```

The skill installs to `skills/workspace-standard/` in your workspace. Your agent will automatically use it when it needs to decide where to write things, add a project, or run maintenance.

### Option 2: Clone from GitHub

```bash
git clone https://github.com/marcus-qen/workspace-standard.git
```

Copy the contents into your OpenClaw workspace's `skills/workspace-standard/` directory:

```bash
cp -r workspace-standard/ ~/.openclaw/workspace/skills/workspace-standard/
```

### Option 3: Just grab the scripts

If you only want the tooling without installing the full skill:

```bash
# Download the scripts
curl -O https://raw.githubusercontent.com/marcus-qen/workspace-standard/main/scripts/workspace-init.sh
curl -O https://raw.githubusercontent.com/marcus-qen/workspace-standard/main/scripts/workspace-audit.sh
chmod +x workspace-init.sh workspace-audit.sh
```

## Usage

### Bootstrap a new workspace

```bash
bash skills/workspace-standard/scripts/workspace-init.sh
```

Creates: `projects/`, `runbooks/`, `memory/entities/`, `skills/`, `MEMORY.md`, seed files with front-matter.

### Add a project

```bash
bash skills/workspace-standard/scripts/workspace-init.sh --project my-saas-app
```

Creates the project directory with README.md (including front-matter), standard subdirectories, and registers it in `projects/_index.md`.

### Audit your workspace

```bash
bash skills/workspace-standard/scripts/workspace-audit.sh
```

Sample output:

```
Auditing workspace: /home/user/.openclaw/workspace

── Root Files ──
✓ AGENTS.md exists
✓ SOUL.md exists
✓ USER.md exists
✓ MEMORY.md exists

── MEMORY.md Budget ──
✓ MEMORY.md: 73 lines (budget: 100)

── Directory Structure ──
✓ memory/ exists
✓ projects/ exists
✓ runbooks/ exists
✓ skills/ exists

── Projects ──
✓ projects/_index.md exists
✓ projects/my-app/README.md exists
✓ projects/my-app/ has standard subdirectories

── Front-Matter ──
✓ All 12 files have front-matter with role

── Summary ──
Workspace is clean. No issues found.
```

Exit code = number of issues. Zero means clean.

### Migrate an existing workspace

> **⚠️ Before you start:** Make sure your workspace is committed to git with no uncommitted changes. Run `git status` first. This way, if anything goes wrong, `git checkout -- .` brings everything back instantly.

If you already have a flat `docs/` directory:

1. **Audit first** — run the audit to see your current state
2. **Review the plan** — ask your agent *"What would you move where? Show me before doing anything"*
3. **Categorise** each file by role (use the decision tree above)
4. **Move files** with `git mv` (preserves history): `git mv docs/my-plan.md projects/my-app/plans/`
5. **Add front-matter** to each moved file
6. **Update path references** in AGENTS.md, MEMORY.md, and any skills that reference `docs/`
7. **Trim MEMORY.md** to ≤100 lines
8. **Commit atomically** — one commit for the whole migration, easy to revert

> **💡 Tip:** You can migrate gradually. Move a few files at a time. The audit will keep showing warnings for files still in `docs/` until they're all moved — that's by design, not pressure.

## Configuration

Create `.workspace-standard.yml` in your workspace root to customise defaults. Everything is optional — sensible defaults apply when omitted.

```yaml
budget:
  memory_lines: 100        # Max lines for MEMORY.md (default: 100)

maintenance:
  stale_days: 14           # Days before flagging active files as stale (default: 14)

projects:
  subdirs:                 # Subdirectories created per project (defaults below)
    - references
    - plans
    - research
    - reports

entities:                  # Seed files created in memory/entities/ (defaults below)
  - people
  - servers
  - decisions
```

**What's configurable:** Numbers (budget, stale threshold) and directory/entity names.

**What's opinionated (the standard):** The 7 roles, front-matter fields, directory structure pattern, maintenance cycle. These are the value of a standard — consistency across deployments.

## Front-Matter

Every substantive markdown file gets a YAML header:

```yaml
---
role: reference
project: my-project
status: current
created: 2026-02-01
updated: 2026-02-19
summary: "One-line description of what this file contains"
---
```

The audit script checks for front-matter, verifies the `role:` field is present, and flags files with `status: current` or `status: active` that haven't been updated within the stale threshold.

**Status lifecycle:** `active` (being worked on) → `current` (living document) → `stale` (needs review) → `archived` (kept for history)

## MEMORY.md Budget

MEMORY.md is loaded into context every session. Every line costs tokens and reduces your agent's reasoning quality.

- **Budget:** ≤100 lines (configurable)
- **Contains:** People, infrastructure summary, project pointers, lookup table, urgent items
- **Does NOT contain:** History, lessons, detailed architecture, completed items, issue lists

When over budget: move detail into project reference files or runbooks. Keep only pointers in MEMORY.md.

## Requirements

- **Bash 4+** (macOS: `brew install bash`)
- **Standard POSIX tools:** find, grep, sed, head, wc, date, mkdir
- **No external dependencies** — no Node, Python, API keys, or package installs
- Works on **Linux** and **macOS** (dual date handling: GNU and BSD)

## Talking to Your Agent

The skill triggers automatically, but you can also ask your agent directly. Here are prompts that work:

### Explore and understand

```
"Show me how the workspace is structured"
"Run a workspace audit and tell me what needs attention"
"What role would this file be? [paste content]"
"Where should I put my notes about comparing deployment tools?"
"Explain the difference between a reference and a report"
```

### Set up and organise

```
"Bootstrap the workspace standard"
"Add a new project called home-automation"
"Migrate my docs/ folder to the new structure"
"Add front-matter to all the files in projects/my-app/"
"My MEMORY.md is too long — help me trim it to budget"
```

### Maintain

```
"Run the weekly maintenance checklist"
"Which files are stale and need updating?"
"Consolidate this week's daily logs into the project references"
"Check if my projects/_index.md is up to date"
```

### Verify and review

```
"Audit the workspace and walk me through every issue"
"Show me what the init script would create before running it"
"What would change if I migrated docs/ to the new structure? Don't do it yet, just show me"
"Dry-run: what would the audit flag on my workspace?"
```

> **Tip:** If you're nervous about changes, always ask the agent to **explain before acting**. Say *"show me what you'd do, don't do it yet"* — any good agent will respect that.

## How the Agent Uses This

Once installed as a skill, your OpenClaw agent automatically reads SKILL.md when it needs to:

- **Decide where to write something** — the "Where to Write" table gives a clear lookup
- **Add a new project** — runs `workspace-init.sh --project`
- **Run maintenance** — follows the maintenance checklist
- **Understand a file's purpose** — front-matter makes every file self-describing

You don't need to tell the agent to use it. The skill triggers automatically based on the task.

## FAQ

**Q: Do I need OpenClaw to use this?**
A: The scripts work standalone. You can use `workspace-init.sh` and `workspace-audit.sh` to structure any markdown-based workspace. The SKILL.md is specifically for OpenClaw's skill system.

**Q: What if I don't like the default subdirectory names?**
A: Create `.workspace-standard.yml` and set your own under `projects.subdirs`. The scripts and audit will use your custom names.

**Q: Can I use this for multiple projects?**
A: That's the whole point. Each project gets its own directory under `projects/`. Run `workspace-init.sh --project <name>` for each one.

**Q: What if I already have a `docs/` directory?**
A: The audit will warn you about it. Follow the migration guide in SKILL.md to categorise and move files to their proper locations.

**Q: How does this differ from the other memory/workspace skills on ClawHub?**
A: Most memory skills focus on vector databases or session state. This skill focuses on *file organisation* — where your agent writes things, how files describe themselves, and how to keep the workspace from becoming a mess over time. It ships actual tooling (init + audit scripts) rather than just documentation.

## Origin

Built out of necessity. After 19 days of running an AI agent on a platform engineering project — 50+ secret migrations, Kyverno policy rollouts, CNPG restore drills, CI/CD automation — the workspace had 39 files in a flat `docs/` directory and a 224-line MEMORY.md that was 2.2× over budget. The restructure took 30 minutes. This skill ensures it never happens again.

## Contributing

Issues and PRs welcome. The standard is opinionated by design — if you want to change the role taxonomy, make a case for why the seven roles don't cover a use case.

## License

MIT
