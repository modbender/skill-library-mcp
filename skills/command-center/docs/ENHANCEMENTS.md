# 🚀 Command Center Enhancements

Prioritized feature backlog based on community research and user needs.

---

## 🔴 P1 — High Impact (Next Sprint)

### 1. Chat Interface

**Source:** klöss prompt, natural UX expectation

Talk to your agent directly from the dashboard.

- Left sidebar: session list (from transcript files)
- Main area: message bubbles with role alignment
- Input bar with send button
- **Stretch:** Voice input via Web Speech API

**Why:** Currently must use Slack/Discord/Telegram. Dashboard-native chat = single pane of glass.

### 2. Models Inventory Panel

**Source:** klöss prompt

Show all available models with:

- Model name + provider
- Current routing rules (which tasks → which model)
- Cost per 1K tokens (input/output)
- Failover chains
- Usage stats

**Why:** Cost visibility is core to Command Center. Models tab completes the picture.

### 3. Knowledge Search

**Source:** klöss prompt, obvious utility

Full-text search across workspace files:

- memory/\*.md
- state/\*.json
- AGENTS.md, TOOLS.md, etc.

**Implementation:** Use ripgrep or native Node fs + fuzzy matching. Return snippets with file paths.

**Why:** "What did we decide about X?" should be answerable from dashboard.

### 4. Live Refresh Indicator

**Source:** klöss prompt UX pattern

Visual indicator showing:

- 🟢 LIVE dot (SSE connected)
- "AUTO 15S" countdown to next update
- Last updated timestamp

**Why:** Users can't tell if data is fresh or stale.

---

## 🟡 P2 — Medium Priority (Roadmap)

### 5. Agent Details Expansion

Currently: Show active sessions per agent
**Enhancement:**

- Read agent's SOUL.md (personality)
- Read agent's config (model, capabilities)
- Show sub-agent spawn tree
- Recent outputs / decisions

### 6. Observations Feed

Parse `state/observations.md` or similar to show:

- What the agent learned today
- Patterns noticed
- Suggestions/insights

**Why:** Agents should surface learnings, not just do tasks.

### 7. Git/Code Status

For power users with coding agents:

- Repos in workspace with branch + dirty count
- Recent commits
- Open PRs (via GitHub API)

### 8. Revenue/Business Tracker

For users monetizing their agents:

- Current revenue
- Monthly burn (API costs)
- Net position
- Savings vs manual estimate

**Why:** klöss prompt shows demand for this in agency/consulting use cases.

### 9. Content Pipeline (Kanban)

For content-generating agents:

- Draft → Review → Approved → Published columns
- Card per content piece
- Approve/reject actions

---

## 🟢 P3 — Nice to Have (Future)

### 10. Calendar Integration

Weekly view of scheduled events:

- Cron jobs mapped to calendar
- Integration with Google Calendar (read-only)

### 11. CRM / Client Pipeline

For consulting/agency use:

- Prospect → Contacted → Meeting → Proposal → Active
- Read from clients/ directory

### 12. Ecosystem View

Multi-product portfolio tracking:

- Product grid with status badges
- Health indicators per product

### 13. Command Palette

Quick command interface (Cmd+K style):

- Trigger cron jobs
- Send quick messages
- Navigate to any panel

---

## 🎨 Design Improvements (Ongoing)

### Glass Card Enhancement

Current cards are solid. Consider:

```css
bg-white/[0.03] backdrop-blur-xl border border-white/[0.06]
```

### Stagger Animations

Add 0.05s delay per card for grid reveals.

### Skeleton Loading

Show loading skeletons instead of spinners.

### Empty States

Friendly messaging when panels are empty.

---

## Implementation Notes

### Our Advantage

- **Zero dependencies** — we're vanilla JS, no build step
- **~200KB total** — theirs will be 5-10MB+
- **Instant startup** — no Next.js cold start

### Their Advantage

- Convex real-time sync
- Framer Motion polish
- More opinionated UX (chat-first)

### Strategy

Cherry-pick features that fit our philosophy:

1. Keep it lightweight
2. Keep it dependency-free
3. Focus on visibility over control
4. Let OpenClaw handle the actions

---

## Feature Voting (Community Input Needed)

| Feature          | Votes | Notes |
| ---------------- | ----- | ----- |
| Chat Interface   | —     |       |
| Models Inventory | —     |       |
| Knowledge Search | —     |       |
| Live Indicator   | —     |       |
| Agent Details    | —     |       |

_Collect votes via GitHub Discussions or Discord poll._

---

_Last updated: 2026-02-13_
_Sources: klöss prompt tweet, Product Hunt research_
