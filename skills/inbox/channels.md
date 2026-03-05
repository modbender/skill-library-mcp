# Multi-Channel Orchestration

## Unified View Principles

Users have inboxes everywhere. The agent creates ONE prioritized view:
- Email (multiple accounts)
- Slack/Discord/Teams (multiple workspaces)
- WhatsApp/Signal/Telegram
- Twitter/LinkedIn/Instagram DMs
- GitHub/GitLab notifications
- Project tools (Asana, Notion, Linear, Jira)
- Calendar invites
- Voice messages

**Never make user check multiple places.** Aggregate, triage, present.

## Channel-Specific Handling

### Email
- Thread summarization for long chains
- Auto-archive newsletters to digest
- Separate transactional (receipts, confirmations) from actionable

### Chat Platforms
- @mention detection is high priority
- Channel noise vs DM distinction
- Thread context preservation across conversations

### Social DMs
- Spam/bot filtering critical
- Opportunity detection (business inquiries, collaborations)
- Sentiment monitoring for reputation issues

### Project Tools
- Blocked/blocking relationship tracking
- Deadline extraction and reminders
- Cross-project dependency awareness

### Calendar
- Conflict detection across calendars
- Auto-decline low-priority with polite response
- Timezone math handling

### Voice Messages
- Transcribe immediately
- Extract action items and deadlines
- Summarize in one line

## Routing Logic

When item arrives:
1. Identify source channel
2. Classify content type
3. Link to project/context if applicable
4. Apply channel-specific rules
5. Merge into unified priority queue

## Context Switching Support

When user shifts focus to a project/client:
- Surface: Last touchpoint, open items, recent decisions
- Show: Relevant threads across ALL channels
- Prepare: Talking points for upcoming meetings
- Alert: Anything aging or at risk

## Follow-Up Automation

Track items waiting for response from others:
- Auto-nudge after configurable interval (default: 5 days)
- Escalating tone in follow-ups (polite → direct → concerned)
- Surface "dead" threads for user decision: archive or final push
