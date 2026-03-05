---
name: openspec-workflow
description: "Autonomous spec-driven development with OpenSpec CLI and Claude Code. You orchestrate (draft artifacts, make judgment calls, ship PRs) while Claude Code reviews with real codebase access and implements tasks. Use when: (1) making any code change in a repo that uses OpenSpec, (2) creating or modifying proposals, designs, specs, or task breakdowns, (3) shipping PRs that need spec artifacts, (4) setting up auto-archive CI for OpenSpec repos. Covers the full lifecycle: issue → OpenSpec artifacts → Claude Code review → Claude Code implementation → PR → auto-archive on merge. Requires: openspec CLI, claude CLI (Claude Code), gh CLI, git."
---

# OpenSpec Workflow

Ship spec-driven changes autonomously with review quality gates.

## Architecture

**You are the orchestrator.** You serve as the "human in the loop" — you make judgment calls, draft spec artifacts, process review feedback, and decide what ships. Claude Code is your hands — it explores the codebase, reviews with real code context, and implements tasks.

| Role | Who | What |
|------|-----|------|
| **Orchestrator** | You (the agent running this skill) | OpenSpec CLI, artifact drafting, review judgment, PR shipping |
| **Reviewer** | Claude Code (or subagent) | Codebase exploration, claim verification, artifact challenges |
| **Implementer** | Claude Code | Task implementation, code changes, commits |

**Why this split:** The OpenSpec CLI is designed for scripting and automation — perfect for an orchestrator. Claude Code gets full codebase context automatically — perfect for review and implementation. The interactive plugin adds friction that doesn't help when an AI is the decision-maker.

## When to Use This Skill

**Use OpenSpec when** the change affects what the product *does*:
- New features or capabilities
- Refactors that change behavior
- Breaking changes or migrations
- Anything that modifies or creates specs

**Skip OpenSpec, just ship a PR when** the change is supplementary:
- Examples, tutorials, sample projects
- Typo fixes, README updates, comment tweaks
- CI/CD config (GitHub Actions, linting)
- Dependency bumps

The key question: *"Does this change what the product does, or just add stuff around it?"*

## Prerequisites

- `openspec` CLI installed (`npm install -g @fission-ai/openspec`)
- `claude` CLI installed (Claude Code)
- `gh` CLI authenticated with repo access
- Git repo with `openspec/` directory initialized
- Working directory is the repo root (or a git worktree)

## Timeouts

When running this workflow as a sub-agent, set `runTimeoutSeconds` based on change size:

| Change type | Timeout | Why |
|-------------|---------|-----|
| Doc-only / trivial | 300 (5 min) | 1-2 artifacts, maybe skip review, quick implementation |
| Standard code change | 900 (15 min) | 4 artifacts × Claude Code review + implementation |
| Large / multi-file | 1200 (20 min) | Complex reviews, big implementation, possible re-reviews |

Each Claude Code invocation (review or implement) takes 1-3 minutes. A full workflow with 4 reviewed artifacts + implementation = 5-8 Claude Code calls minimum.

## Quick Start

```
1. openspec new change "<name>"
2. For each artifact: draft → review loop → write
3. Implement tasks
4. Commit, push, open PR with "OpenSpec change: <name>" in body
```

## Workflow

### Step 1: Create the Change

```bash
openspec new change "<kebab-case-name>"
openspec status --change "<name>"
```

### Step 2: Artifact Loop

For each artifact in order (typically: proposal → design → specs → tasks):

```bash
openspec instructions <artifact-id> --change "<name>"
```

Read the template and dependencies. Draft the artifact content.

**Then decide: review or skip?**

- **Skip review** if the artifact is genuinely trivial (one-liner, obvious config, mechanical rename). Log: `Skipped review — trivial: <reason>`.
- **Send to review** for anything with real design decisions, trade-offs, or ambiguity.

Spawn reviewers as subagents with the **repo path** so they can explore the codebase independently — read files, grep for patterns, verify "no code changes" claims. Don't just paste the artifact; give them the tools to challenge it. See `references/review-loop.md` for the full protocol and prompt template.

After writing the artifact, confirm progress:

```bash
openspec status --change "<name>"
```

Continue to the next artifact.

### Step 3: Implement via Claude Code

**Do not implement tasks directly.** Delegate to Claude Code, which has full codebase context and can make changes safely.

```bash
# Get the task list for Claude Code's prompt
cat openspec/changes/<name>/tasks.md
```

Launch Claude Code in the repo (or worktree) with PTY and `--dangerously-skip-permissions`:

```bash
exec pty:true workdir:<repo-path> background:true command:"claude --dangerously-skip-permissions -p 'Implement these tasks from openspec/changes/<name>/tasks.md. Read the tasks file, the proposal, design, and specs in that change directory for full context. Mark tasks complete as you go. Commit when done.

When completely finished, run: openclaw system event --text \"Done: implemented <name>\" --mode now'"
```

Monitor via `process action:log sessionId:<id>`. Claude Code will:
- Read the OpenSpec artifacts for context
- Implement each task
- Mark `[x]` as it goes
- Commit the changes

For trivial changes (pure doc edits, one-line fixes), you may implement directly instead. Log: `Implemented directly — trivial: <reason>`.

### Step 4: Ship

**Before committing**, verify the change name matches the actual directory:

```bash
# Get the exact change directory name
CHANGE=$(ls openspec/changes/ | grep -v archive | head -1)
echo "Change name: $CHANGE"
```

Use this exact name everywhere — commit message AND PR body:

```bash
git add -A
git commit -m "<type>(scope): <description> (#<issue>)

OpenSpec change: $CHANGE"
git push origin <branch>
gh pr create --repo <owner/repo> --base main --head <branch> \
  --title "<type>: <description>" \
  --body "Closes #<issue>

OpenSpec change: $CHANGE"
```

**Critical:** The `OpenSpec change: <name>` in the PR body must **exactly match** the directory name under `openspec/changes/`. The auto-archive GitHub Action uses this to locate the change. A mismatch means the archive silently skips. Always verify with `ls openspec/changes/` before writing the PR body.

### Step 5: Address PR Review Comments

After opening the PR, code review agents may leave comments. Monitor and respond:

```bash
# Check for review comments
gh pr view <number> --repo <owner/repo> --json reviews,comments
gh api repos/<owner>/<repo>/pulls/<number>/comments
```

For each review comment:

1. **Evaluate** — Is it significant? Does it catch a real bug, missing edge case, or design issue?
2. **If significant:** Fix it in the worktree, commit, push. The PR updates automatically.
   ```bash
   # Fix, then:
   git add -A && git commit -m "fix: address review — <what changed>"
   git push origin <branch>
   ```
3. **If not significant:** Reply inline with your justification.
   ```bash
   gh api repos/<owner>/<repo>/pulls/<number>/comments/<comment-id>/replies \
     -f body="<your justification>"
   ```

Apply the same judgment rules as the artifact review loop: accept valid concerns, reject with reasoning, partially accept where appropriate. Don't blindly apply every suggestion — you're the decision-maker.

### Step 6: Document & Report

Post the workflow log to the GitHub issue:

```bash
gh issue comment <number> --repo <owner/repo> --body '<workflow log>'
```

Include: each artifact's draft, review challenges, revisions, skip decisions with reasoning, and final implementation notes.

**Always end by linking the user to the issue and PR:**
- Issue: `https://github.com/<owner>/<repo>/issues/<number>`
- PR: `https://github.com/<owner>/<repo>/pull/<number>`

## Artifact Guidelines

### proposal.md
- **Why** (1-2 sentences), **What Changes** (bullet list), **Capabilities** (new + modified specs), **Impact**
- List every spec that will be created or modified in Capabilities — this drives the specs artifact

### design.md
- **Context**, **Goals / Non-Goals**, **Decisions** (with alternatives considered), **Risks / Trade-offs**
- Skip for trivial changes (pure doc fixes, one-line config changes)

### specs/\<capability\>/spec.md
- Delta format: `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`
- Every requirement needs `### Requirement: <name>` + at least one `#### Scenario:`
- MODIFIED must include the full updated requirement text (not just the diff)
- Use existing spec names from `openspec/specs/` for modified capabilities

### tasks.md
- Numbered groups with checkboxes: `- [ ] 1.1 Task description`
- Small enough to complete in one session
- Ordered by dependency

## GitHub Action: Auto-Archive on Merge

For repos that want automatic spec sync and archiving, add this workflow. See `references/archive-action.md` for the complete GitHub Action YAML.

The action:
1. Triggers on PR merge
2. Extracts change name from `OpenSpec change: <name>` in PR body
3. Runs `openspec archive --yes` on a new branch
4. Opens a PR with the archive and spec sync changes
5. Deletes the original merged branch
