---
name: team-status-tracker
description: Systematic team status tracking via Slack DMs with confidential Obsidian-based internal tracking. Maintains confidentiality while gathering actionable project updates from team members.
metadata:
  {
    "tags": ["slack", "team-management", "status-tracking", "obsidian", "confidentiality"],
    "openclaw":
      {
        "requires": { "skills": ["slack", "obsidian"] }
      }
  }
---

# Team Status Tracker via Slack

## Overview

Systematic approach to track team member status updates via Slack DMs with Obsidian-based internal tracking. Maintains confidentiality while gathering actionable project updates.

## When to Use

- Daily/weekly team status check-ins
- Project progress monitoring
- Resource management and workload tracking
- Identifying blockers and support needs
- Behavioral pattern analysis for team optimization

## Key Principles

### Communication (Slack DMs)
✅ **DO:**
- Send personalized status requests (1-on-1 DMs)
- Ask specific questions about THEIR projects only
- Request task IDs, timelines, specific blockers
- Maintain professional, supportive tone
- Offer help with blockers
- Follow up with non-responders (mid-day, EOD)

❌ **DON'T:**
- Share financial information with resources (unless `finance_transparency: 1` - see Configuration)
- Share billing amounts, revenue figures, client contracts (unless explicitly enabled)
- Discuss other team members' performance publicly
- Share behavioral tracking notes with team (NEVER - always confidential)
- Use public channels for status requests (keep it private)

### Internal Tracking (Obsidian)
✅ **Track (Confidential):**
- Response times (prompt, delayed, no response)
- Response quality (detailed, vague, minimal)
- Behavioral patterns (proactive, reactive, non-responsive)
- Communication effectiveness
- Blockers and support needs

❌ **Never Share with Team:**
- These tracking notes
- Performance comparisons
- Response time metrics
- Non-responder lists

## Configuration

### config.yaml

Create a configuration file at `.openclaw/workspace/skills/team-status-tracker/config.yaml`:

```yaml
# Team Status Tracker Configuration

# Confidentiality Settings
confidentiality:
  # Financial information transparency
  # 0 = NEVER share financial info (billing, revenue, payments) with resources (DEFAULT)
  # 1 = Share financial context when needed (budget, project value, payment status)
  finance_transparency: 0
  
  # What to NEVER share regardless of transparency setting
  always_confidential:
    - Performance comparisons between team members
    - Behavioral tracking notes
    - Response time metrics
    - Non-responder lists
    - Internal strategy discussions

# Slack Settings
slack:
  check_interval_hours: 2  # How often to check for responses
  reminder_midday: true    # Send mid-day reminder to non-responders
  reminder_eod: true       # Send end-of-day reminder
  
# Response Grading
response_grading:
  excellent: "<1h"
  good: "1-3h"
  acceptable: "3-6h"
  delayed: "6-12h"
  poor: ">12h"
```

### Using the Config

**When `finance_transparency: 0` (DEFAULT - Recommended):**

❌ **DON'T share:**
- "This project is worth $50K"
- "Client is paying us $X/month"
- "You'll get paid when invoice clears"
- "Project budget is $XXX"
- "Client owes us money"

✅ **DO share:**
- "This project is high priority"
- "Client needs this urgently"
- "This is a strategic client"
- General project scope and timeline

**When `finance_transparency: 1` (Optional - Use with caution):**

✅ **CAN share when contextually relevant:**
- "This project has a budget of $X - keep scope tight"
- "Client pays milestone-based, need to deliver by [date] for payment"
- "High-value client ($XX/month) - prioritize their requests"
- "We're waiting on client payment before next phase"

❌ **STILL DON'T share:**
- Individual team member salaries or rates
- Performance comparisons
- Behavioral tracking notes
- Full contract terms
- Client's internal budget/financials

### When to Enable Finance Transparency

**Consider `finance_transparency: 1` when:**
- ✅ Working with senior team members (leads, managers)
- ✅ Team owns P&L responsibility
- ✅ Budget constraints affect decisions
- ✅ Payment delays impact work planning
- ✅ Team needs context for scope/priority decisions

**Keep `finance_transparency: 0` when:**
- ✅ Junior team members (default safe option)
- ✅ Contractors/outsourced resources
- ✅ Large team with varied seniority
- ✅ Uncertain about team maturity
- ✅ Company policy requires strict separation

### Message Examples by Config

**Scenario:** Team member asks about project priority/urgency

**With `finance_transparency: 0` (DEFAULT):**
```
This is a strategic client for us - high priority.
Please prioritize their requests and maintain quality.
Let me know if you need any support!
```

**With `finance_transparency: 1`:**
```
This is a high-value client ($X/month contract).
Project budget is $Y - keep scope tight and deliver by [date].
Payment is milestone-based, so meeting the deadline is critical.
Let me know if scope creep becomes an issue!
```

---

**Scenario:** Team member asks why project is urgent

**With `finance_transparency: 0`:**
```
Client needs this urgently for their Q1 launch.
It's a strategic partnership opportunity.
Can you prioritize this over [other project]?
```

**With `finance_transparency: 1`:**
```
Client needs this for Q1 launch - they've paid 50% upfront ($X).
Remaining $Y comes on delivery by [date].
Can you prioritize this? It's blocking our cash flow.
```

---

**Scenario:** Team member asks about changing scope

**With `finance_transparency: 0`:**
```
Let's stick to the original scope for now.
Any additions need client approval first.
Please document the request and I'll discuss with client.
```

**With `finance_transparency: 1`:**
```
Current scope is fixed at $X - no room in budget.
If they want additions, we need to quote separately.
Please document the request with time estimate.
I'll discuss pricing with client.
```

## Process

### 1. Morning: Send Status Requests

Send personalized Slack DMs asking ONLY about specific person's projects:

```
Hi [Name]! 👋

Quick status check on *[Their Project]*:

📊 Could you please share:
• Current progress this week?
• Any blockers or challenges?
• Coordination with team smooth?
• Support needed?

Thanks! 🚀
```

**Key Rules:**
- ✅ Personalize for each person's actual projects
- ✅ Ask specific questions
- ❌ NO commercial/payment info
- ❌ Don't mention other projects they're not on

### 2. Throughout Day: Monitor & Respond

**Check Slack every 2-3 hours:**

When someone responds:
1. Read their response in Slack
2. Ask follow-up questions via Slack:
   ```
   Thanks for the update! 👍
   
   Could you provide:
   📋 Specific task ID or ticket number?
   📊 Current progress % or milestone?
   ⏰ Expected completion date?
   🚧 Any blockers preventing progress?
   ```
3. Update internal Obsidian tracking
4. Never share confidential info in responses

When no response by mid-day:
```
Hi [Name]! 👋

Just a friendly reminder - still waiting for your status update.

Would appreciate a quick response when you get a chance. Thanks! 🙏
```

### 3. End of Day: Final Nudge

For non-responders:
```
Hi [Name]! ⏰

Quick reminder - please share your status update by end of day today.

This helps us track progress and provide support. Thanks! 🙏
```

### 4. Track in Obsidian (Internal Only)

Create daily tracking files:

```
daily-status/
├── YYYY-MM-DD/
│   ├── TEAM STATUS - YYYY-MM-DD.md
│   └── SUMMARY.md
└── README.md (confidentiality rules)
```

**Track for each person:**
- Response time
- Response quality
- Behavioral pattern
- Project updates
- Blockers mentioned
- Follow-up needed

## Response Time Benchmarks

- **Excellent:** < 1 hour
- **Good:** 1-3 hours
- **Acceptable:** 3-6 hours (same day)
- **Delayed:** 6-12 hours
- **Poor:** > 12 hours or no response

## Behavioral Categories

### 🟢 Proactive
- Responds quickly
- Provides detailed updates
- Anticipates questions
- Asks for clarification when needed

### 🟡 Reactive  
- Responds when prompted
- Basic updates provided
- Needs follow-up questions

### 🔴 Non-Responsive
- Delayed or no responses
- Vague or incomplete updates
- Requires multiple nudges

## Confidentiality Rules

### 🚫 ALWAYS CONFIDENTIAL (Regardless of Config):
- Performance comparisons between team members
- Behavioral tracking notes
- Response time metrics
- Non-responder lists
- Internal strategy discussions

### 💰 FINANCIAL INFO (Config-Dependent):

**When `finance_transparency: 0` (DEFAULT):**
❌ DON'T share: Payment amounts, billing, revenue, budgets, client contracts

**When `finance_transparency: 1` (OPTIONAL):**
✅ CAN share: Project budgets, payment milestones, scope constraints (when contextually relevant)
❌ STILL DON'T share: Individual rates, profit margins, full contracts, client's financials

### ✅ ALWAYS OK to Share:
- Project requirements and technical details
- Task assignments and deadlines
- Team coordination information
- General project status and priority
- Technical support and guidance

## Example Daily Workflow

**08:00 UTC** - Send personalized status requests to 12 team members via Slack DMs

**10:00 UTC** - Check Slack responses:
- 2 responded → Ask for task IDs, update Obsidian
- 10 no response → Send mid-day reminder

**14:00 UTC** - Check again:
- 5 more responded → Follow up, update tracking
- 5 still pending → Note as delayed

**17:00 UTC** - EOD check:
- 8 total responded
- 4 non-responders → Send EOD reminder, flag for next day

**18:00 UTC** - Final tracking update:
- Document response rates
- Note behavioral patterns
- Plan next day's approach
- Keep all internal notes confidential

## Integration with Obsidian

Create this structure in your PKM:

```markdown
# /root/life/pkm/daily-status/

## README.md
- Confidentiality rules
- Process guidelines
- Response benchmarks

## YYYY-MM-DD/
### TEAM STATUS - YYYY-MM-DD.md
Individual tracking per person:
- Response time
- Quality assessment
- Behavioral notes
- Project updates
- Action items

### SUMMARY.md
- Overall response rate
- Key observations
- Critical non-responders
- Next steps
```

## Tools Integration

### Slack API (via Maton Gateway)
```bash
# List users
curl -X GET "https://gateway.maton.ai/slack/api/users.list" \
  -H "Authorization: Bearer $MATON_API_KEY"

# Send DM
curl -X POST "https://gateway.maton.ai/slack/api/chat.postMessage" \
  -H "Authorization: Bearer $MATON_API_KEY" \
  -d '{"channel": "USER_ID", "text": "Message"}'

# Get conversation history
curl -X GET "https://gateway.maton.ai/slack/api/conversations.history?channel=CHANNEL_ID" \
  -H "Authorization: Bearer $MATON_API_KEY"
```

### Obsidian Skills
Use the `obsidian` skill to create and update daily tracking notes automatically.

## Success Metrics

- Response rate > 80% within 6 hours
- Average response time < 3 hours
- Clear task IDs and timelines provided
- Blockers identified early
- Proactive communication increasing over time

## Lessons Learned

1. **Personalization matters**: Generic messages get ignored, specific project questions get responses
2. **Confidentiality is critical**: Never share commercial/payment info with resources
3. **Multiple nudges work**: Mid-day + EOD reminders significantly improve response rates
4. **Document behavior**: Patterns emerge over time, useful for resource management
5. **Private DMs only**: Public status requests create comparison anxiety
6. **Ask for specifics**: "Making progress" is useless, "Task ID #123, 70% done, due Friday" is actionable

## Related Skills

- `slack` - Slack integration for messaging
- `obsidian` - PKM system for tracking notes
- `team-management` - Broader team management approaches

## Version History

- **1.0.0** (2026-02-27) - Initial version with Slack + Obsidian integration, confidentiality rules

---

**Author:** Real-world team status tracking implementation
**License:** MIT
**Tags:** slack, team-management, status-tracking, obsidian, confidentiality
