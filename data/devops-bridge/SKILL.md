---
name: devops-bridge
description: >
  Unified developer operations bridge connecting GitHub, CI/CD (GitHub Actions), Slack, Discord, and
  issue trackers (Linear, Jira, GitHub Issues) into cross-tool automated workflows. Sends context-rich
  CI failure notifications to Slack with failing test details, tracks PR review lifecycle with escalating
  reminders, generates daily dev standup summaries, syncs issue status when PRs are merged, detects
  flaky tests, and monitors repository health. Use this skill for: PR review reminders, CI build alerts,
  "what happened in my repos", "any failing builds", "who needs a review", dev team standup summary,
  deploy notifications, repository monitoring, connecting GitHub to Slack, linking PRs to Jira/Linear
  tickets, code review tracking, merge conflict alerts, or any request to bridge development tools
  together. If the user mentions GitHub AND Slack (or any two dev tools) together, this skill connects them.
metadata:
  openclaw:
    emoji: "🔧"
---

# DevOps Bridge

The missing link between your dev tools. This skill connects GitHub, CI/CD, Slack/Discord, and issue trackers into workflows that actually make sense — so you stop context-switching between 6 browser tabs.

## Why This Exists

Developers already use separate skills for GitHub, Slack, etc. But nobody has built the bridge: when CI fails, automatically link it to the PR, notify the right Slack channel, and update the ticket. This skill is that bridge.

## Core Capabilities

### 1. Smart Notifications

Transform noisy GitHub events into actionable, context-rich messages. Instead of "Build failed", deliver:

```
🔴 CI Failed — PR #142 "Add OAuth flow" by @alice
  └─ Test: auth.test.ts:47 — Expected 200, got 401
  └─ Last passing commit: abc1234 (2 hours ago)  
  └─ Linked issue: LINEAR-389 "Implement SSO"
  └─ Action: Reply "fix" to see the failing test, "logs" for full output
```

When sending notifications, always:
- Include the PR title and author, not just the number
- Link to the specific failing test or check, not just "CI failed"
- Mention the last known good commit for quick bisect context
- Cross-reference related issues/tickets if they exist
- Suggest a concrete next action

### 2. PR Review Management

Track pull request lifecycle across tools:

**Review reminders:**
- Scan open PRs daily and flag those waiting for review
- Escalate based on age: gentle reminder at 24h, stronger at 48h, urgent at 72h+
- Send reminders to the assigned reviewer via Slack/Discord DM or channel
- Format:
  ```
  👀 Review needed:
  • PR #142 "Add OAuth flow" — waiting 3 days (assigned: @bob)
  • PR #156 "Fix pagination" — waiting 1 day (assigned: @carol)
  ```

**Review status sync:**
- When a PR gets approved on GitHub, post to the team channel
- When changes are requested, notify the author directly
- When all checks pass + approved, prompt: "Ready to merge — want me to merge it?"

### 3. CI/CD Intelligence

Go beyond "pass/fail" with intelligent CI analysis:

- **Failure grouping**: if multiple PRs fail on the same test, flag it as a systemic issue rather than spamming individual notifications
- **Flaky test detection**: if a test fails intermittently across PRs, note it: "This test has failed 3 times this week across different PRs — likely flaky"
- **Duration tracking**: "This build took 45 min, up from the usual 20 min — something may be wrong"
- **Auto-retry suggestion**: for known flaky failures, suggest or trigger a re-run

### 4. Issue Tracker Sync

Keep issue trackers (Linear, Jira, GitHub Issues) in sync with actual development activity:

- When a PR references an issue (e.g., "Fixes #123"), update the issue status automatically
- When a PR is merged, move the linked issue to "Done" or "In Review"
- When CI fails on a PR linked to an issue, add a comment to the issue noting the blocker
- Surface orphaned PRs: "PR #167 doesn't reference any issue — should it?"

### 5. Daily Dev Standup

Generate a team-level development summary on demand or via cron:

```
🧑‍💻 Dev Standup — [Date]

Merged yesterday:
  • PR #140 "Refactor auth module" by @alice → LINEAR-385 closed
  • PR #143 "Update deps" by @bob

In review:
  • PR #142 "Add OAuth flow" by @alice — 2 approvals, CI passing ✅
  • PR #156 "Fix pagination" by @carol — changes requested by @bob

Blocked:
  • PR #158 "Migrate DB" by @dave — CI failing (migration timeout)
  • Issue LINEAR-402 — no assignee, due tomorrow

CI Health: 87% pass rate (down from 94% last week)
  └─ Flaky: auth.test.ts (failed 4/10 runs)
```

## Configuration

### Required Tools
- `gh` CLI (GitHub) — for repo activity, PRs, issues, CI status
- At least one messaging channel configured (Slack, Discord, Telegram)

### Optional Tools
- Linear CLI or API — for Linear issue tracking
- Jira API — for Jira integration  
- GitHub Issues — works out of the box with `gh`

### Setup Flow

On first use, gather configuration interactively:

1. **Which repos to monitor?** Ask for a list or use "all repos I have push access to"
2. **Where to send notifications?** Slack channel, Discord channel, Telegram, or all
3. **How aggressive should reminders be?** Options: gentle (72h), moderate (48h), aggressive (24h)
4. **Include CI details?** Some users want full logs, others just pass/fail
5. **Who's on the team?** Map GitHub usernames to Slack/Discord handles for @mentions

Store configuration in workspace memory for persistence.

### Cron Setup

Suggest these default schedules (user can customize):

```json
[
  {
    "name": "Morning dev digest",
    "schedule": "0 9 * * 1-5",
    "prompt": "Generate dev standup summary for my repos"
  },
  {
    "name": "PR review reminder",  
    "schedule": "0 14 * * 1-5",
    "prompt": "Check for PRs waiting for review and send reminders"
  },
  {
    "name": "End of day CI report",
    "schedule": "0 17 * * 1-5",
    "prompt": "Summarize today's CI/CD activity and flag any issues"
  }
]
```

## Command Reference

Users can trigger specific actions with natural language:

| User says | Action |
|-----------|--------|
| "What's happening in my repos?" | Full activity summary across all monitored repos |
| "Any failing builds?" | CI status check with details on failures |
| "Who needs a review?" | List PRs awaiting review with age and assignee |
| "Standup" | Generate daily dev standup summary |
| "Notify #dev-team about PR 142" | Send a formatted notification about a specific PR |
| "Link PR 142 to LINEAR-389" | Create cross-reference between PR and issue |
| "Set up CI alerts for repo X" | Configure monitoring for a specific repository |
| "Merge PR 142" | Merge if all checks pass and approved; warn if not |

## Edge Cases

- **Monorepo**: if monitoring a monorepo, group notifications by directory/team, not just by PR
- **Forks**: when PRs come from forks, note this clearly (different trust level)
- **Draft PRs**: don't send review reminders for draft PRs unless user asks
- **Stale PRs**: if a PR has been open >7 days with no activity, suggest closing or rebasing
- **Rate limits**: GitHub API has rate limits. Batch requests and cache results within a session
- **No messaging configured**: if no Slack/Discord/Telegram, output to the current conversation instead
- **Multiple orgs**: if user has repos across multiple GitHub orgs, handle them all but label clearly

## Integration Pattern

This skill works best with other installed skills. When detected:
- **github skill**: defer raw GitHub operations to it, use devops-bridge for cross-tool logic
- **slack skill**: use it for message delivery, devops-bridge composes the messages
- **daily-briefing-hub**: feed dev activity data into the morning briefing's "Dev Activity" section
