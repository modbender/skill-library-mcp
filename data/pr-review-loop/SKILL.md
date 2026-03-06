---
name: pr-review-loop
description: Autonomous PR review loop with Greptile. Use when an agent creates a PR and needs to autonomously handle code review feedback — reading Greptile reviews, fixing issues, pushing fixes, re-triggering review, and auto-merging when score is 4/5+. Trigger on commands like "pr review {url}", "review my PR", or when a Greptile review webhook/poll delivers feedback.
---

# PR Review Loop

Autonomous cycle: Greptile reviews PR → agent fixes feedback → pushes → re-triggers → repeats until score ≥ 4/5 or max rounds.

## Quick Start

When triggered with a PR URL or review payload:

```bash
# Run the review loop
bash scripts/pr-review-loop.sh <owner/repo> <pr-number>
```

Or invoke steps manually — see below.

## Workflow

### 1. Fetch Review

```bash
# Get latest Greptile review
gh api "/repos/{owner}/{repo}/pulls/{pr}/reviews" \
  --jq '[.[] | select(.user.login == "greptile-apps[bot]")] | last'

# Get inline comments
gh api "/repos/{owner}/{repo}/pulls/{pr}/comments" \
  --jq '[.[] | select(.user.login == "greptile-apps[bot]")]'
```

### 2. Parse Score

Look for confidence/quality score in review body. Greptile typically includes a score like `Score: X/5` or `Confidence: X/5`. Extract it:

- **Score ≥ 4/5** → auto-merge
- **Score < 4/5** → fix issues
- **No score found** → treat as needing fixes if there are comments, otherwise merge

### 3. Auto-Merge (score ≥ 4)

```bash
gh pr merge <number> --merge --delete-branch --repo <owner/repo>
```

### 4. Fix Issues (score < 4)

For each Greptile comment:
1. Read the file and line referenced
2. Understand the feedback
3. Apply the fix
4. Stage changes

Commit with a descriptive message listing each fix:
```
Address Greptile review feedback (round N)

- Fix X in path/to/file.ts
- Fix Y in path/to/other.ts
- Improve Z per reviewer suggestion
```

Push and re-trigger:
```bash
git push
gh pr comment <number> --repo <owner/repo> --body "@greptileai review"
```

### 5. Track State

Maintain `review-state.json` in workspace:
```json
{
  "owner/repo#123": {
    "rounds": 2,
    "maxRounds": 5,
    "lastScore": 3,
    "sameScoreCount": 1
  }
}
```

Update after each round. Check exit conditions:
- **rounds ≥ 5** → merge anyway, notify Master
- **sameScoreCount ≥ 2** (same score 2 rounds in a row) → merge anyway, notify Master

### 6. Escalation

- **Architectural decisions** (review mentions architecture, design patterns, breaking changes) → ping Master on Telegram, don't auto-fix
- **Max rounds reached** → merge + notify Master with summary
- **Unclear feedback** → ask Master

## Command Interface

Agents should respond to:
- `pr review <url>` — start review loop on a PR
- `pr review <owner/repo#number>` — same, by reference
- `pr status` — show active review loops and their state

## References

See `references/greptile-patterns.md` for common Greptile feedback patterns and fix strategies.
