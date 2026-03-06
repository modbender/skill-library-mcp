# MEMORY.md — Long-Term Memory

# ⚠️ HARD LIMIT: Keep this file under 3,500 characters.
# It is injected into every session. Over the limit = silent truncation.
# Agent loses context without knowing it. Keep it tight.

## Who I Am
- **Name:** [AGENT_NAME] | **Born:** [DATE]
- **Human:** [YOUR_NAME] (Telegram: @[handle], id: [ID])

## [Your Name]
- Timezone: [YOUR_TIMEZONE]
- [Key fact that should survive every session restart]
- [Key fact that should survive every session restart]
- "[trigger phrase]" = [what it means — e.g. "afk" = start working from mission queue]
- Values: [what matters most — proactive? confirms? flags breaks immediately?]

## Platform
- **Primary channel:** [Telegram/Signal/etc.]
- [Group ID if using a group]
- [Topic IDs if using Telegram topics — format: 63 (Ops), 64 (Security), etc.]
- Cron delivery format: `GROUP_ID:topic:THREAD_ID`

## Infrastructure
- [Your machine] | Gateway: [port] (loopback)
- Models: [model assignments per agent]
- [Any critical infrastructure fact worth remembering across sessions]

## Agents
- [List each agent with role and model]

## Key Lessons
[Leave mostly empty at start — this section fills in as patterns emerge.]
[The 3 AM memory consolidation cron will promote recurring lessons here automatically.]
