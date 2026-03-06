# Approval Workflow

How content moves from draft to published. This workflow prepares for future auto-posting capability.

---

## Pipeline Stages

```
[DRAFT] → [PENDING APPROVAL] → [APPROVED] → [SCHEDULED/POSTED]
                ↓                    ↓
            [REVISION]          [REJECTED]
```

### 1. DRAFT
- Agent creates content and tags it `[DRAFT]`
- Internal stage — user doesn't see drafts unless reviewing the pipeline

### 2. PENDING APPROVAL
- Agent presents content to user with `[PENDING APPROVAL]` tag
- Content includes: copy, hashtags, visual brief, platform, scheduled time
- User must explicitly respond

### 3. User Response Options
- **"approve"** or **"looks good"** → Status moves to `[APPROVED]`
- **"revise [feedback]"** → Status moves to `[REVISION]`, agent re-drafts with feedback
- **"reject"** or **"skip this"** → Status moves to `[REJECTED]`, content is discarded

### 4. APPROVED
- Content is confirmed and ready for posting
- Currently: user posts manually
- Future: auto-posting will execute at scheduled time

### 5. SCHEDULED/POSTED
- Content has been published
- Log the posting in daily memory notes

## Telegram Topic Routing

Route approval items to the correct brand topic. See `shared/operations/channel-map.md` for the full channel map and delivery rules.

## Rules

1. **No content is ever posted without explicit user approval.**
2. Agents must tag all external-facing content with `[PENDING APPROVAL]`.
3. Approval is per-item — bulk approval is allowed when user says "approve all".
4. Stale approvals (>48h without response) should be flagged by Leader.
5. Maximum 2 attempts total (original + 1 revision). If the revision is also rejected, escalate to Leader for discussion with user.
6. **Multi-agent rework**: When content goes through review + rework loops across multiple agents, the final output still requires explicit user approval before any external action. Rework between agents does not bypass this workflow.
7. **Route approvals to the correct brand topic** — never send one brand's approvals to another brand's topic.

## Approval Shortcuts

The user can use these shortcuts in conversation:
- `approve` / `lgtm` / `ship it` — approve the most recent pending item
- `approve all` — approve all pending items
- `revise: [feedback]` — request changes with specific feedback
- `reject` / `kill it` / `nah` — reject the most recent pending item
- `show queue` — list all pending approval items

## Reviewer Integration

- **Leader-initiated**: Leader invokes Reviewer at its discretion (campaign launches, high-stakes content, rework failures, etc.)
- **Owner-requested**: Owner explicitly asks for a review — Leader must invoke Reviewer
- Reviewer provides `[APPROVE]` or `[REVISE]`
- Leader evaluates Reviewer feedback as a peer, not as a directive
- Leader may override Reviewer (must document reason in daily notes)
- Maximum 2 review rounds per task
- After review, Leader includes a brief review summary in the response (what was flagged, action taken, verdict)

---

_This workflow will evolve as auto-posting capabilities are connected._
