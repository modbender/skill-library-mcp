---
name: improve-skill
description: >-
  Meta-skill: evaluate any Factory Droid skill against the current project codebase
  and suggest concrete improvements. Use when: a skill feels incomplete, produces
  suboptimal results, doesn't cover edge cases in the current project, or the user
  wants to tighten skill-project fit. Analyzes skill definition, supporting files,
  invocation history, and codebase structure to produce actionable upgrade recommendations.
user-invocable: true
disable-model-invocation: false
---

# Improve Skill — The Meta-Skill

Evaluate an existing Factory Droid skill against the current project codebase and produce concrete, prioritized improvement recommendations.

## When to Use

- After first invocation of a skill — "that worked, but it missed X"
- When a project evolves and a skill hasn't kept up
- When onboarding a skill from another project into a new codebase
- When the user says "make this skill better" or "this skill doesn't handle Y"
- Auto-invocable: the droid can suggest improvements after observing skill friction

## Inputs

When invoked, determine which skill to evaluate:

1. **Explicit**: `/improve-skill ghost-catalog` — user names the skill
2. **Contextual**: If the user just invoked a skill and says "improve it" — use the last invoked skill
3. **Discovery**: If no skill is named, list all installed skills and ask which one to evaluate

## Evaluation Framework

Run these 6 analyses in order. For each, produce findings and a verdict (STRONG / ADEQUATE / WEAK / MISSING).

### 1. Skill Definition Audit

Read the skill's `SKILL.md` and all supporting files.

Check for:
- **Clarity**: Are instructions unambiguous? Could a droid follow them without guessing?
- **Completeness**: Are all commands documented with inputs, outputs, and edge cases?
- **Structured inputs**: Does the skill define what it expects (paths, flags, formats)?
- **Success criteria**: Does the skill define what "done" looks like?
- **Error handling**: Does the skill say what to do when things fail?
- **Verification step**: Does the skill require confirmation that it worked?

Report gaps as specific line-level observations, not vague suggestions.

### 2. Codebase Fit Analysis

Scan the current project to understand its shape:

- **File types**: What extensions exist? Does the skill handle all of them?
- **Directory structure**: How deep? How many top-level dirs? Does the skill's path logic match?
- **Naming conventions**: camelCase, kebab-case, PascalCase? Does the skill respect them?
- **Framework patterns**: Next.js App Router, Flask blueprints, monorepo? Does the skill understand the framework?
- **Scale**: How many files? Does the skill handle the volume efficiently (batch vs one-by-one)?

Identify **blind spots** — file types, directories, or patterns the skill doesn't account for but the project uses.

### 3. Edge Case Discovery

Look for things that would break or confuse the skill:

- **Unusual files**: Files with no extension, dotfiles, generated files, symlinks
- **Encoding issues**: Non-UTF-8 files, BOM markers, mixed line endings
- **Directive conflicts**: `'use client'`, shebangs (`#!/usr/bin/env`), pragma comments (`@ts-nocheck`)
- **Framework magic**: Auto-generated files (`.next/`, `__generated__/`), barrel exports (`index.ts`)
- **Binary in source dirs**: Images in `public/`, fonts in `assets/`, SQLite in `data/`
- **Monorepo patterns**: Multiple `package.json`, nested `.gitignore`, workspace configs

For each edge case found in the current project, note whether the skill handles it.

### 4. Output Quality Assessment

If the skill has been invoked before and produced artifacts (files, DB entries, reports), evaluate them:

- **Accuracy**: Are generated descriptions meaningful or generic ("Module for foo")?
- **Consistency**: Same patterns get same treatment across the codebase?
- **Completeness**: Did it miss any files it should have caught?
- **Formatting**: Headers well-formed? DB entries normalized? Reports readable?

If no prior invocation exists, simulate a dry run by analyzing what the skill WOULD produce for 5-10 representative files.

### 5. Composability Check

How well does this skill play with others?

- **Data output**: Does it produce machine-readable output other skills can consume?
- **Idempotency**: Safe to run twice? Does it detect prior runs?
- **State management**: Where does it store state? Is that documented?
- **Cross-skill hooks**: Could other skills trigger this one? Could this one feed into others?
- **Token efficiency**: Does the skill load too much context? Could supporting files be trimmed?

### 6. User Experience Review

From the user's perspective:

- **Invocation friction**: Is `/skill-name` enough or does the user need to remember flags?
- **Feedback quality**: Does the skill report what it did clearly?
- **Progressive disclosure**: Can a user start simple and go deeper?
- **Recovery**: If the skill makes a mistake, how hard is it to undo?
- **Documentation**: Could a new user understand the skill from SKILL.md alone?

## Output Format

After running all 6 analyses, produce a structured improvement report:

```
SKILL IMPROVEMENT REPORT
========================
Skill:    [name]
Project:  [current project]
Date:     [today]
Agent:    [agent_id]

SCORECARD
---------
1. Definition Clarity:   [STRONG/ADEQUATE/WEAK/MISSING]
2. Codebase Fit:         [STRONG/ADEQUATE/WEAK/MISSING]
3. Edge Case Coverage:   [STRONG/ADEQUATE/WEAK/MISSING]
4. Output Quality:       [STRONG/ADEQUATE/WEAK/MISSING]
5. Composability:        [STRONG/ADEQUATE/WEAK/MISSING]
6. User Experience:      [STRONG/ADEQUATE/WEAK/MISSING]

Overall: [X/6 STRONG]

TOP IMPROVEMENTS (prioritized by impact)
-----------------------------------------
1. [HIGH] Title
   Problem: ...
   Fix: ...
   Effort: [trivial / small / medium / large]

2. [HIGH] Title
   Problem: ...
   Fix: ...
   Effort: ...

3. [MEDIUM] Title
   ...

EDGE CASES FOUND IN THIS PROJECT
----------------------------------
- [handled/unhandled] Description

SUGGESTED SKILL.MD PATCHES
----------------------------
[Specific text additions/changes to the skill definition]
```

## After the Report

Ask the user which improvements to implement. Then:

1. Edit the skill's `SKILL.md` with the approved changes
2. Add or update supporting files if needed
3. Re-run the skill on a sample of files to verify the improvement
4. Update the improvement report with results

## Auto-Invocation Guidance

This skill should be considered when:
- A user says "that didn't work right" or "it missed something" after a skill runs
- A skill produces generic or inaccurate output
- The user asks "how can we make this better"
- The droid observes repeated manual corrections after a skill invocation
- A skill is being used in a project type it wasn't originally designed for

## Principles

- **Be specific, not vague**: "Add .vue to the CMP category in line 47 of SKILL.md" not "consider more file types"
- **Prioritize by impact**: What change helps the most files / saves the most tokens / prevents the most errors?
- **Show evidence**: Every finding should reference a specific file, line, or pattern in the project
- **Respect the user's design**: Improve the skill's execution of its stated purpose, don't redesign it
- **Measure before and after**: If possible, show what changes quantitatively (files caught, accuracy %, etc.)
