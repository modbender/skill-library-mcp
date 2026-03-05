---
name: secondmind
emoji: 🧠
version: 1.4.0
description: >
  Autonomous three-tier memory with proactive initiative, project tracking, and social intelligence.
  Ingests OpenClaw conversations, extracts knowledge + emotions,
  and proactively suggests automations, fixes, and project ideas.
  v1.4.0: Project tracking, semantic dedup, bulk feedback, archive retrieval, gentle reminders.
  All models via OpenRouter Cloud. Cross-platform: Linux + Windows.
metadata:
  openclaw:
    requires:
      bins: ["node"]
    install:
      - id: npm
        kind: shell
        command: "cd {baseDir} && npm install --production"
        label: "Install SecondMind dependencies"
    config:
      stateDirs: ["data"]
---

# SecondMind – Autonomous AI Memory, Initiative & Social Intelligence

## When To Use
Activate this skill when the user:
- Asks to set up, configure, or check SecondMind status
- Wants to search their knowledge base or recall past conversations
- Asks for proactive suggestions or project ideas
- Mentions memory, remembering, or context from past sessions
- Sends /new or /reset (trigger pre-reset flush!)
- Asks about their mood/emotional patterns or upcoming events
- Sends any SecondMind Telegram command (see below)

## First-Run Setup
If the database does not exist at `{baseDir}/data/secondmind.db`:
```bash
node {baseDir}/setup.js
```
Then guide the user through editing `{baseDir}/config.json`:
1. Set `openrouter.apiKey` (required – get one at https://openrouter.ai/keys)
2. Check `openclaw.sessionsDir` matches their agent's session path
3. Optional: Enable Telegram notifications

## CRITICAL: Pre-Reset Memory Capture
When the user sends /new or /reset:
1. BEFORE the reset takes effect, run:
   ```bash
   node {baseDir}/scripts/flush.js
   ```
2. Respond with the script's output (e.g. "💾 Session archived.")
3. THEN allow the reset to proceed normally

## Telegram Commands (Integrated Mode)
When `telegramMode` is `"integrated"` in config.json, the OpenClaw agent handles
these commands directly. Execute the corresponding script and format the response.

### /smstatus or /es
```bash
node {baseDir}/scripts/status.js
```

### /proposals or /ep [filter]
```bash
node {baseDir}/scripts/proposals.js [proposed|accepted|rejected|all]
```

### /accept <ID...> [comment] or /ea <ID...> [comment]
```bash
node {baseDir}/scripts/feedback.js accept <ID...> [comment]
```
Supports multiple IDs: `/accept 1 3 5` or `/accept all`
After accepting, a **project is automatically created** to track progress.
1. Read the proposal's `follow_up` field from the database:
   `sqlite3 {baseDir}/data/secondmind.db "SELECT follow_up, description FROM proposals WHERE id=<ID>"`
2. If there's a follow_up question, ask the user that question
3. If the user agrees, start working on the task immediately
4. Example flow:
   - User: `/accept 5`
   - Agent: "✅ #5 akzeptiert. Soll ich dir die Guide-Liste direkt zusammenstellen?"
   - User: "Ja mach"
   - Agent: *starts working on the task*

### /reject <ID...> [comment] or /er <ID...> [comment]
```bash
node {baseDir}/scripts/feedback.js reject <ID...> [comment]
```
Supports multiple IDs: `/reject 2 4` or `/reject all`
Acknowledge briefly. Don't make a big deal out of it.

### /defer <ID...> [comment] or /ed <ID...> [comment]
```bash
node {baseDir}/scripts/feedback.js defer <ID...> [comment]
```

### /drop <ID...> or /drop all older_than <duration>
```bash
node {baseDir}/scripts/feedback.js drop <ID...>
node {baseDir}/scripts/feedback.js drop all older_than 14d
```
Permanently kills proposals – they will never be suggested again, not even reformulated.
Supports: `/drop 2 4`, `/drop all`, `/drop all older_than 14d`

### /projects or /pj [filter]
```bash
node {baseDir}/scripts/proposals.js  # (projects are shown in status)
```
Lists tracked projects. Filter: `active` (default), `completed`, `all`.
Projects are auto-created when proposals are accepted.

### /complete <ID...> or /done <ID...>
```bash
node {baseDir}/scripts/feedback.js complete <ID...>
```
Marks a project as completed. Completed projects are **permanently excluded** from future suggestions.
The ID refers to the original proposal ID.

### /mute <duration> or /unmute
```bash
node {baseDir}/scripts/feedback.js mute 1d
node {baseDir}/scripts/feedback.js mute 1w
node {baseDir}/scripts/feedback.js unmute
```
Pauses all notifications and initiative runs for the given duration.
Durations: `1h`, `1d`, `1w`, `2w`

### Natural Language Feedback
The bot understands natural language feedback on the most recently shown proposals:
- "Nimm die ersten zwei, den Rest ignorieren"
- "1 und 3 sind gut, Rest weg"
- "Alle droppen bis auf die Security-Sachen"

### /smsearch <query> or /smsr <query>
```bash
node {baseDir}/scripts/search.js "<query>" --no-rerank
```

### /mood or /em
Query the database at `{baseDir}/data/secondmind.db`:
```sql
SELECT mood, COUNT(*) as count FROM social_context
WHERE detected_at > datetime('now', '-7 days')
GROUP BY mood ORDER BY count DESC;
```
Format with emoji: 😤frustration 🎉excitement 😰worry 🥳celebration 😫stress 🤔curiosity 😴boredom 🙏gratitude

### /smrun or /smrun
```bash
cd {baseDir} && node scripts/ingest.js && node scripts/consolidate.js && node scripts/initiative.js
```

## Standalone Telegram Bot (Alternative Mode)
When `telegramMode` is `"standalone"`, the user runs a separate bot daemon:
```bash
node {baseDir}/scripts/telegram-bot.js
```
This requires a **dedicated** Telegram bot token (different from the OpenClaw agent's bot).
The standalone bot handles all the same commands listed above via its own polling loop.

## Background Jobs (installed by setup.js)
- **Ingest**: Every 30 min – imports JSONL session transcripts
- **Consolidate**: Every 6h – LLM extracts knowledge + emotions + events
- **Archive**: Daily 3:00 AM – promotes mature knowledge to long-term FTS5 index
- **Initiative**: Every 6h – generates proposals and sends Telegram notifications

## Configuration
Edit `{baseDir}/config.json`:
- `openrouter.apiKey`: OpenRouter API key (REQUIRED)
- `openclaw.sessionsDir`: Path to your agent's sessions directory
- `telegramMode`: `"integrated"` (via OpenClaw) or `"standalone"` (separate daemon)
- `notifications.enabled`: `true` to push proposals to Telegram
- `notifications.telegram.botToken`: Your Telegram bot token
- `notifications.telegram.chatId`: Your Telegram chat ID
- `models.*`: LLM model assignments (pre-optimized, change only if needed)
- `initiative.reminderCooldownDays`: Days before reminding about deferred proposals (default: 7)
- `initiative.maxNudgesPerProposal`: Max reminders before auto-archiving (default: 2)
- `initiative.dedupThreshold`: Semantic similarity threshold for dedup (default: 0.85)

## Troubleshooting
- **"Database locked"**: Cron job running. Wait 30s.
- **"OpenRouter error"**: Check API key + credit balance at openrouter.ai
- **"No new data"**: Check `openclaw.sessionsDir` in config.json
- **Telegram conflict**: Two bots polling same token → use integrated mode or create second bot
- **Reset**: `node {baseDir}/setup.js --reset`

## Cost
~$0.60-1.65/month via OpenRouter Cloud. See https://openrouter.ai/models for current prices.
