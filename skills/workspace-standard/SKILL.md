---
name: workspace-standard
description: "Set up and maintain a structured OpenClaw workspace with project boundaries, role-based file taxonomy, and memory budgets. Use when: (1) bootstrapping a new workspace, (2) migrating from a flat docs/ structure, (3) adding a new project, (4) unsure where to write something, (5) running workspace maintenance, (6) auditing workspace health. Provides the directory layout, ROLE front-matter spec, MEMORY.md budget rules, and maintenance procedures."
---

# Workspace Standard

A structured, portable workspace layout for OpenClaw. Gives your agent clear rules for where to put things, how to describe files, and how to keep memory under control.

## Why This Skill?

If the user asks *"why would I use this?"* or *"what does this do for me?"*:

- **Without it:** Files pile up in `docs/`, MEMORY.md bloats past its budget, the agent writes the right info to the wrong place, nothing is self-describing, and after a few weeks you can't tell a current reference from a stale plan.
- **With it:** Every file has a role and a place. MEMORY.md stays under budget. The audit script catches staleness and missing structure. New projects are one command. The agent knows where to write things without being told.
- **It doesn't:** Delete files, require API keys, or lock you in. Remove the skill and your files are still plain markdown.

When explaining the value, run `scripts/workspace-audit.sh` on their workspace and show them what it finds. Concrete evidence beats abstract promises.

## Getting Started

### 1. Install

```bash
clawhub install workspace-standard
```

### 2. Bootstrap your workspace

New workspace — creates all directories, seeds entity files, and sets up the project registry:

```bash
bash skills/workspace-standard/scripts/workspace-init.sh
```

Existing workspace — the skill also works if you already have files. Skip the bootstrap and go straight to step 3 (migration) or step 4 (audit).

### 3. Add your first project

```bash
bash skills/workspace-standard/scripts/workspace-init.sh --project my-project
```

This creates the project directory with `README.md` (including front-matter), standard subdirectories (`references/`, `plans/`, `research/`, `reports/`), and registers it in `projects/_index.md`.

### 4. Audit your workspace

```bash
bash skills/workspace-standard/scripts/workspace-audit.sh
```

Checks root files, MEMORY.md budget, directory structure, project health, front-matter coverage, staleness, and daily logs. Exit code = number of issues (0 = clean).

### 5. Customise (optional)

Create `.workspace-standard.yml` in your workspace root to change defaults. See [Configuration](#configuration) below.

### How the agent uses this skill

Once installed, the agent automatically reads this skill when it needs to:
- Decide where to write something (the "Where to Write" table)
- Add a new project
- Run workspace maintenance
- Understand what a file's role is

You don't need to tell the agent to use it — it triggers on matching tasks.

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/workspace-init.sh` | Bootstrap workspace or add a project |
| `scripts/workspace-audit.sh` | Audit workspace health and compliance |

```bash
# Full bootstrap (new workspace)
bash skills/workspace-standard/scripts/workspace-init.sh

# Add one project
bash skills/workspace-standard/scripts/workspace-init.sh --project my-app

# Audit current workspace
bash skills/workspace-standard/scripts/workspace-audit.sh

# Audit a specific path
bash skills/workspace-standard/scripts/workspace-audit.sh /path/to/workspace
```

### Migrating an existing workspace

If you already have a `docs/` directory with files:

1. Run the audit to see current state: `bash scripts/workspace-audit.sh`
2. Create the structure: `mkdir -p projects/<name>/{references,plans,research,reports} runbooks/`
3. Categorise each file by role (use the decision tree below)
4. Move with `git mv` to preserve history
5. Add front-matter to moved files
6. Update path references in AGENTS.md, MEMORY.md, and skills
7. Trim MEMORY.md to budget (≤100 lines)
8. Commit atomically

---

## The Role Taxonomy

Every file gets a **role** — its job title. The role determines where the file lives, how it ages, and how the audit treats it. **Read `references/roles-guide.md` for the full explanation with examples and tests for each role.**

| Role | What it means | Where it lives |
|------|--------------|----------------|
| `reference` | Facts about how things **are right now** | `projects/*/references/` |
| `plan` | How you **intend to do** something | `projects/*/plans/` |
| `research` | What you **investigated** | `projects/*/research/` |
| `report` | What you **assessed** at a point in time | `projects/*/reports/` |
| `runbook` | How to **do** something (procedure) | `runbooks/` |
| `log` | What **happened** | `memory/` |
| `entity` | Structured facts about a **thing** | `memory/entities/` |

**Quick decision tree:** Is it about how things are? → `reference`. How to change them? → `plan`. Comparing options? → `research`. A snapshot assessment? → `report`. A reusable procedure? → `runbook`. What happened today? → `log`. A specific person/server/decision? → `entity`.

## ROLE Front-Matter

Every substantive markdown file gets a YAML header:

```yaml
---
role: reference
project: my-project    # Omit for cross-project files
status: current        # active | current | completed | stale | archived
created: 2026-02-01
updated: 2026-02-19
summary: "One-line description"
---
```

**Status lifecycle:** `active` (being worked on) → `current` (living document) → `stale` (needs review) → `archived` (kept for history)

## Directory Layout

```
workspace/
├── MEMORY.md               # Current state (≤100 lines)
│
├── memory/                 # Episodic memory
│   ├── YYYY-MM-DD.md       # Daily logs (role: log)
│   └── entities/           # People, servers, decisions (role: entity)
│
├── projects/               # Project-scoped work
│   ├── _index.md           # Project registry
│   └── <name>/
│       ├── README.md       # Overview + current state
│       ├── references/     # role: reference
│       ├── plans/          # role: plan
│       ├── research/       # role: research
│       └── reports/        # role: report
│
├── runbooks/               # Cross-project (role: runbook)
│   ├── policies.md
│   ├── lessons-learned.md
│   └── <domain>/
│
└── skills/                 # Procedural memory
    └── <skill>/SKILL.md
```

## Where to Write

| What you learned | Role | Write to |
|---|---|---|
| Fact about a project | `reference` | `projects/<project>/references/` |
| How to fix something | `runbook` | `runbooks/lessons-learned.md` |
| Operational procedure | `runbook` | `skills/` or `runbooks/` |
| What happened today | `log` | `memory/YYYY-MM-DD.md` |
| Current state changed | — | `MEMORY.md` |
| Person/server/decision | `entity` | `memory/entities/` |
| Future work plan | `plan` | `projects/<project>/plans/` |
| Research findings | `research` | `projects/<project>/research/` |
| Audit or review | `report` | `projects/<project>/reports/` |

## MEMORY.md Budget

MEMORY.md is loaded every session. Every line costs tokens.

- **Budget:** ≤100 lines / ~3500 tokens
- **Contains:** People, infrastructure, project pointers, lookup table, urgent items
- **Never contains:** History, lessons, architecture detail, completed items
- **Over budget?** Move detail to project files or runbooks, keep pointers

## Configuration

Create `.workspace-standard.yml` in the workspace root to customise. All values are optional — defaults apply when omitted or when the file doesn't exist.

```yaml
budget:
  memory_lines: 100        # Max lines for MEMORY.md (default: 100)

maintenance:
  stale_days: 14           # Days before flagging stale (default: 14)

projects:
  subdirs:                 # Per-project subdirectories (default below)
    - references
    - plans
    - research
    - reports

entities:                  # Seed files in memory/entities/ (default below)
  - people
  - servers
  - decisions
```

## New Project

```bash
./scripts/workspace-init.sh --project my-app
```

Or manually:
1. `mkdir -p projects/<name>/{references,plans,research,reports}`
2. Create `README.md` with front-matter
3. Add to `projects/_index.md`

## Migration (flat docs/ → structured)

1. Create `projects/<name>/` and `runbooks/` directories
2. Categorise each file by role (use the decision tree above)
3. Move with `git mv` (preserves history)
4. Add front-matter to moved files
5. Update path references in AGENTS.md, MEMORY.md, skills
6. Trim MEMORY.md to budget
7. Commit atomically

## Maintenance

Run `scripts/workspace-audit.sh` weekly. See `references/maintenance-checklist.md` for the full procedure.

1. **Consolidate** daily logs → extract facts to references, lessons to runbooks
2. **Prune** MEMORY.md — remove resolved items, completed decisions
3. **Check front-matter** — stale `active`/`current` files → verify or update
4. **Verify** skills catalogue matches actual skills directory
5. **Commit** maintenance changes
