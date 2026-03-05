---
name: pr-ship
description: Pre-ship risk report for OpenClaw PRs. Dynamically explores the codebase to assess module risk, blast radius, and version-specific gotchas. Scores each finding by severity (🟢/🟡/🔴). Updated frequently with the latest OpenClaw version context — run `clawhub update pr-ship` regularly to stay current.
---

# pr-ship

## Overview

Pre-ship risk report for **[OpenClaw](https://github.com/openclaw/openclaw)** pull requests.

This skill is **updated frequently** to track OpenClaw releases. The version-specific context (gotchas, behavioral changes, active risk areas) is refreshed with each upstream release. Run `clawhub update pr-ship` periodically to get the latest context.

What it does:
- Diffs your current branch against `main` in the OpenClaw repository.
- Dynamically investigates each changed module using grep/find/git on the codebase itself.
- Produces a structured risk report with evidence-backed findings scored by severity (🟢/🟡/🔴).
- No approve/reject gate -- just information for you to decide what to fix before publishing.

## Reference Layers

Load these files from the `references/` directory. Each serves a distinct purpose:

1. **`STABLE-PRINCIPLES.md`** -- Timeless OpenClaw coding standards: testing guide, file naming, safety invariants, common pitfalls, PR practices.

2. **`ARCHITECTURE-MAP.md`** -- OpenClaw structural context: module hierarchy, risk tier definitions with calibrated thresholds, critical path patterns, cross-module coupling, change impact matrix.

3. **`CURRENT-CONTEXT.md`** *(optional)* -- Version-specific gotchas, recent behavioral changes, and active risk areas. If this file exists, load it. It tracks the current OpenClaw release.

4. **`EXPLORATION-PLAYBOOK.md`** -- Dynamic investigation procedures. Read-only commands (grep, find, ls, git) that discover the current state of the OpenClaw codebase.

5. **`VISION-GUIDELINES.md`** -- Project vision, contribution policy, and merge guardrails derived from OpenClaw's VISION.md. Covers PR scope rules, security philosophy, plugin/core boundary, skills policy, MCP strategy, and the explicit "will not merge" list. Use this to catch policy and architectural misalignment.

STABLE-PRINCIPLES, ARCHITECTURE-MAP, EXPLORATION-PLAYBOOK, and VISION-GUIDELINES should always be present. CURRENT-CONTEXT is optional -- if missing, the skill still works but without version-specific gotcha awareness.

## Workflow

### 1. Load reference layers
- Read the four reference files listed above.

### 2. Collect diff against `main`
- Get current branch: `git branch --show-current`
- Gather file list: `git diff --name-only main...HEAD`
- Gather patch content: `git diff main...HEAD`

### 3. Classify changed modules
- For each changed file, identify its `src/<module>/` path.
- Look up the module's risk tier in ARCHITECTURE-MAP.md.
- If the module isn't listed or you want to verify, run the dynamic consumer count from EXPLORATION-PLAYBOOK.md "Dynamic Risk Classification" section.

### 4. Run dynamic exploration per changed module
- Follow EXPLORATION-PLAYBOOK.md "Blast Radius Discovery" for each changed file.
- Follow "Module-Specific Investigation Strategies" for each changed module type.
- Follow "Test Discovery" to identify relevant tests.
- Check "Red Flags Table" against the diff.

### 5. Evaluate findings
- Compare exploration evidence against:
  - Safety invariants and common pitfalls from STABLE-PRINCIPLES.md
  - Version-specific gotchas from CURRENT-CONTEXT.md (if loaded)
  - Architecture coupling patterns from ARCHITECTURE-MAP.md
  - Contribution policy, merge guardrails, and architectural direction from VISION-GUIDELINES.md
- Check PR scope against Vision contribution rules (one PR = one topic, size limits, bundling policy).
- Check for "will not merge" category matches from VISION-GUIDELINES.md section 7.
- Evaluate whether new capabilities respect the plugin/core boundary and security philosophy.
- Every finding must include:
  - **Evidence** from the diff (file + snippet)
  - **Exploration evidence** (command output showing blast radius, consumers, or pattern match)
  - **Reference** to the specific principle, gotcha, or coupling pattern it relates to

### 6. Produce report
- Use the report format below.
- Do not output "approved/rejected".

## Severity and Alert Scoring

- 🟢 **Low Risk** (score 1-2)
  Minor observation, style preference, or informational note. Safe to ship as-is.

- 🟡 **Attention Needed** (score 3-6)
  Partial mismatch, ambiguity, missing hardening, or non-blocking inconsistency. Worth reviewing but unlikely to cause breakage.

- 🔴 **High Risk** (score 7-10)
  Clear conflict with OpenClaw coding standards, architecture patterns, or version-specific constraints. Likely to cause bugs, regressions, or policy violations.

Scoring:
- Score each finding individually (1-10).
- `final_alert_score = max(per_finding_scores)`. If no findings, `final_alert_score = 0`.

## Report Format

```markdown
## pr-ship report

- Branch: `<current-branch>`
- Base: `main`
- Files changed: `<N>`
- Modules touched: `<list with risk tiers>`
- Findings: `<N>`
- Final alert score: `<0-10>`

### Module Risk Summary

| Module | Risk Tier | Consumers | Files Changed |
| --- | --- | --- | --- |
| <module> | CRITICAL/HIGH/MEDIUM/LOW | <N> | <N> |

### Findings

1. 🟢/🟡/🔴 Title
   - Alert: `<1-10>`
   - Reference: `<principle, gotcha, or pattern from reference docs>`
   - Evidence in diff: `<file + short snippet/description>`
   - Exploration evidence: `<what dynamic investigation revealed>`
   - Why this matters: `<1-2 lines>`
   - Suggested fix: `<1-2 concrete actions>`

(repeat)

### Executive summary
- `<short practical summary for decision>`
- `<top 1-3 actions before publishing PR>`
```

## Constraints

- This skill is for the **OpenClaw repository only**. Do not use it on other projects.
- Review only the current branch diff against `main`.
- Do not review unrelated repository history.
- Do not auto-edit code unless explicitly asked.
- Do not convert the report into an approve/reject decision unless explicitly requested.
- Exploration commands are **read-only** (grep, find, ls, git diff). Never execute build, test, or code generation commands -- recommend them to the user in findings instead.

## Provenance

- **Source:** [github.com/Glucksberg/pr-ship](https://github.com/Glucksberg/pr-ship)
- **Maintainer:** Markus Glucksberg ([@Glucksberg](https://github.com/Glucksberg))
- **Update mechanism:** `CURRENT-CONTEXT.md` metadata is refreshed daily via cron when OpenClaw upstream `CHANGELOG.md` changes. GitHub repo is updated separately by the maintainer.
- **Verification:** The GitHub repo is the canonical source of truth. To verify your installed copy matches:

```bash
# Quick: compare file list + versions
diff <(clawhub list | grep pr-ship) <(curl -s https://api.github.com/repos/Glucksberg/pr-ship/contents/package.json | jq -r '.content' | base64 -d | jq -r .version)

# Full: diff your local install against GitHub
SKILL_DIR="$(find ~/.openclaw/skills -maxdepth 1 -name pr-ship -type d 2>/dev/null || echo skills/pr-ship)"
for f in SKILL.md package.json references/CURRENT-CONTEXT.md; do
  diff <(cat "$SKILL_DIR/$f") <(curl -s "https://raw.githubusercontent.com/Glucksberg/pr-ship/main/$f") && echo "$f: ✔ match" || echo "$f: ✘ differs"
done
```

## Security Notice

Reports generated by this skill may include diffs and grep output from your local repository. If your config files, environment, or code contain secrets (API keys, tokens, credentials), those values may appear in the report. **Do not publish or share generated reports without reviewing them for sensitive data first.**

## Credits

Original DEVELOPER-REFERENCE.md format and approach adapted from [mudrii](https://github.com/mudrii)'s developer reference methodology. The dynamic exploration approach was designed based on feedback from the OpenClaw maintainer community.
