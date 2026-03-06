---
name: x-agent
description: "Plan and run X (Twitter) operations in three modes: (1)
  monitor-only intelligence, (2) draft-and-approve posting, and (3) limited
  automation with strict guardrails. Use when setting up X account workflows,
  drafting posts/replies/threads, defining safety policy, scheduling content, or
  reviewing performance."
---


# X Agent (Phased Setup)

## Objective
Operate an X workflow safely across three phases, with automation disabled until explicitly enabled.

## Phase 1 — Monitor-only
1. Track topics, keywords, and accounts.
2. Summarize notable posts and sentiment.
3. Produce a daily/weekly brief:
   - top signals
   - opportunities
   - reputational risks
4. Do not post.

## Phase 2 — Draft + approval
1. Generate draft tweets/replies/threads from user goals.
2. Enforce style rules:
   - concise
   - no unverifiable claims
   - no legal/financial guarantees
3. Present final draft with:
   - risk flags
   - confidence level
   - suggested posting window
4. Require explicit approval before publishing.

## Phase 3 — Limited automation (default OFF)
Enable only after user confirmation.

Automation constraints:
1. Allowed actions only from pre-approved playbooks.
2. Hard caps:
   - max posts/day
   - max replies/hour
3. Blocked categories:
   - politics (unless explicitly allowed)
   - legal/medical/financial advice language
4. Quiet hours and cooldowns required.
5. Global kill switch required.

## Required Guardrails
Always define these before posting access:
1. Account scope: monitor | draft+approve | limited-auto
2. Max daily posts
3. Max hourly replies
4. Quiet hours (timezone)
5. Banned topics/phrases
6. Kill switch command and owner

## Starter Playbooks
1. News reaction post (single tweet)
2. Research summary thread (3–5 posts)
3. Reply triage (approve queue)
4. Daily recap post

## Rollout Checklist
1. Create or choose X account.
2. Configure API credentials in local environment (never in chat).
3. Start in monitor-only for 3–7 days.
4. Move to draft+approve for 1–2 weeks.
5. Enable limited automation for one playbook only.
6. Review weekly and adjust limits.

## Output Formats
### Monitor brief
- What happened
- Why it matters
- Suggested response

### Draft package
- Draft text
- Variant A/B
- Risk flags
- Recommended time

### Automation report
- Actions executed
- Actions skipped (and why)
- Rate limit usage
- Any policy violations blocked
