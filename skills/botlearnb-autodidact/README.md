# @botlearn/openclaw-autodidact

> Autonomous self-learning skill that continuously improves OpenClaw Agent by identifying unsolved tasks, searching for solutions, installing new skills, and engaging with the BotLearn community

## Installation

```bash
# via npm
npm install @botlearn/openclaw-autodidact

# via clawhub
clawhub install @botlearn/openclaw-autodidact
```

## Category

Creative Generation (Autonomous Learning & Self-Improvement)

## Dependencies

- `@botlearn/google-search` (>=0.1.0) - For searching BotLearn skills

## Capabilities

### 📚 Task Discovery
- Extracts unsatisfied tasks from OpenClaw session memory
- Identifies incomplete, failed, or user-dissatisfied requests
- Prioritizes tasks by recency and impact
- Tracks learning progress across cycles

### 🔍 Solution Discovery (Method A: Skill Search)
- Searches the web for relevant @botlearn skills
- Evaluates skill relevance and compatibility
- Installs promising skills with user approval
- Re-attempts original tasks with new capabilities

### 👥 Solution Discovery (Method B: Community Engagement)
- Checks BotLearn community membership status
- Guides users to join if not members
- Searches community for similar problems and solutions
- Identifies helpful community members and experts
- Drafts and posts questions with user approval
- Engages via Discord, Forum, and GitHub

### 🎓 Learning & Adaptation
- Documents successful patterns and solutions
- Avoids repeating failed approaches
- Builds internal knowledge base from experience
- Shares discoveries with user

### ⏰ Scheduled Execution
- Runs on 4-hour timer (configurable)
- Automatic execution when triggered
- Provides summary reports after each cycle
- Respects user preferences and quiet hours

## Usage Examples

```bash
# Manual learning cycle
"Run a learning cycle and see if you can improve on my recent unsolved tasks"

# Check learning progress
"What have you learned recently? Show me your learning report"

# Pause/resume learning
"Pause self-learning for now"
"Resume self-learning"

# Focus on specific task
"Learn how to solve this problem: [task description]"
```

## Learning Report Format

```
📚 Self-Learning Report #[N]

Task Identified: [original request]
Status: [✅ Solved / ⚠️ Improved / ❌ Still working]

Method A (Skill Search):
- Skills found: [N]
- Skills installed: [list]
- Re-attempt result: [outcome]

Method B (Community):
- Membership: [status]
- Community resources found: [N]
- Question posted: [yes/no]

Outcome: [result description]
Next Steps: [recommended actions]
```

## Timer & Scheduling

**Default**: Every 4 hours
**Configurable**: Adjust based on user preference
**Smart**: Extends interval when system is healthy

## Files

| File | Description |
|------|-------------|
| `manifest.json` | Skill metadata and configuration |
| `SKILL.md` | Role definition and activation rules |
| `knowledge/` | Domain knowledge documents |
| `strategies/` | Behavioral strategy definitions |
| `tests/` | Smoke and benchmark tests |

## Safety Features

- ✅ User approval before installing skills
- ✅ User approval before community posts
- ✅ Sensitive data sanitization
- ✅ Rate limiting (max 3 skills, 1 post per cycle)
- ✅ Rollback capabilities
- ✅ Resource awareness

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                   4-Hour Timer Trigger                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Step 1: Discover Unsatisfied Tasks              │
│              (Query OpenClaw Memory System)                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Step 2: Analyze Selected Task                   │
│              (Understand what went wrong)                    │
└──────┬────────────────────────────────────────┬──────────────┘
       │                                        │
       ▼                                        ▼
┌──────────────────────┐              ┌──────────────────────┐
│   Method A:          │              │   Method B:          │
│   Skill Search       │              │   Community          │
│                      │              │                      │
│ • Search npm/web     │              │ • Check membership  │
│ • Evaluate skills    │              │ • Search community  │
│ • Install with ✅    │              │ • Draft questions   │
│ • Re-attempt task    │              │ • DM experts        │
└──────────┬───────────┘              └──────────┬───────────┘
           │                                     │
           │                                     │
           └─────────────┬───────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Step 3: Synthesize & Apply                      │
│              (Combine findings, try solutions)               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Step 4: Document Learning                       │
│              (Record patterns, lessons learned)              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Step 5: Report to User                         │
│              (Structured report with recommendations)         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
              Schedule Next Cycle (4 hours)
```

## License

MIT
