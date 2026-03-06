---
name: knowledgebase-share
description: Operate a multi-agent shared knowledge layer backed by one GitHub repository. Use when setting up shared/private knowledge folders, enforcing branch+PR workflow, syncing branches, resolving merge conflicts, and standardizing how agents write/promote knowledge.
---

# Knowledgebase Share

Use this skill as the **single operating system** for multi-agent knowledge storage.

## Privacy rule (critical)

This is a reusable/public skill. **Never hardcode user-specific repo URLs, paths, or secrets in SKILL.md.**
Always read config from `references/kb-config.json` (or user-provided override) before executing.

## Required config

Read `references/kb-config.json` first.

Fields:
- `repo_url`: canonical GitHub repo URL for knowledge storage
- `local_path`: local clone path
- `branch`: default branch (usually `main`)
- `private_root`: private notes root folder (default `private`)
- `shared_root`: shared notes root folder (default `shared`)

## Repository model

```text
<knowledge-repo>/
  private/<agent>/
  shared/
    00_rules/
    10_projects/
    20_research/
    30_decisions/
    40_playbooks/
    90_archive/
  meta/
  templates/
```

## Branch model

- `main`: stable shared knowledge
- `agent/<name>`: per-agent working branch
- Shared knowledge enters `main` only via PR

## Operating rules

1. Pull/rebase before writing: `git pull --rebase origin <branch>`
2. Keep private drafts in `private/<agent>/`
3. Promote reusable content to `shared/` via PR
4. Never force-push `main`
5. No secrets/tokens in repository content
6. Resolve conflicts by preserving both versions first, then refactor

## Standard flows

### A) Agent daily write (private)
1. checkout `agent/<name>`
2. write to `<private_root>/<name>/...`
3. commit + push branch

### B) Promote to shared knowledge
1. copy/refine note into `<shared_root>/...`
2. commit on `agent/<name>`
3. open PR to `main`
4. merge after review

### C) Consume latest shared knowledge
1. checkout local branch
2. `git fetch origin`
3. rebase from latest `main`

## Minimal commands (template)

```bash
# first-time clone
git clone <repo_url> <local_path>

# create agent branch
cd <local_path>
git checkout -b agent/<name>

# sync branch
git pull --rebase origin agent/<name>

# push updates
git push origin agent/<name>
```

## Boundary

- This skill governs **knowledge layer** operations only.
- Constitution / hard governance rules are maintained in the independent constitution system.
