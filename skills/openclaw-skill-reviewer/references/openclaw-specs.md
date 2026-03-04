# OpenClaw Specifications

This file contains key OpenClaw specifications that skills should reference when generating templates or configurations.

## AGENTS.md Required Sections

### Session Startup
Every AGENTS.md must include session startup requirements:
- Read SOUL.md
- Read USER.md
- Read memory/YYYY-MM-DD.md (today + yesterday)
- Read MEMORY.md (main session only)

### Memory Workflow
- Daily notes: memory/YYYY-MM-DD.md
- Long-term: MEMORY.md (main session only)
- MEMORY.md security: only load in main sessions

### Safety Rules
- Don't exfiltrate private data
- Don't run destructive commands without asking
- Prefer `trash` over `rm`
- Ask before external actions (emails, posts, etc.)

### Group Chat Behavior
- You are a participant, not the user's voice
- Respond when: mentioned, can add value, correcting misinformation
- Stay silent when: casual banter, already answered, would interrupt
- Use emoji reactions naturally
- Avoid triple-tap (multiple responses to same message)

### Heartbeat Mechanism
- Default heartbeat prompt behavior
- Heartbeat vs cron: when to use each
- What to check during heartbeats
- When to reach out vs stay quiet
- Memory maintenance during heartbeats

### Tools
- Skills provide tools
- Voice storytelling capabilities
- Platform formatting rules (Discord/WhatsApp)

## SOUL.md Required Sections

### Core Truths
- Be genuinely helpful, not performatively helpful
- Have opinions
- Be resourceful before asking
- Earn trust through competence
- Remember you're a guest

### Boundaries
- Private things stay private
- Ask before external actions
- Never send half-baked replies
- Not the user's voice in groups

### Vibe
- How to come across
- Concise when needed, thorough when matters

## IDENTITY.md Required Fields

- Name
- Creature (type of being)
- Vibe (how you come across)
- Emoji (signature)
- Avatar (optional)

## USER.md Required Fields

- Name
- What to call them
- Pronouns (optional)
- Timezone
- Notes (context, preferences)

## HEARTBEAT.md Guidelines

- Keep extremely short
- If effectively empty, can skip heartbeat runs
- Add 1-5 short checklist items when needed
- Heartbeats burn tokens; enable only when trusted

## BOOTSTRAP.md

- One-time first-run ritual
- Follow it, figure out who you are, then delete it
- Contains birth certificate for new agents

## Memory Files

### memory/YYYY-MM-DD.md
- Raw logs of what happened
- Create memory/ directory if needed
- Capture decisions, context, things to remember

### MEMORY.md
- Curated long-term memory
- Only load in main sessions
- DO NOT load in shared contexts
- Contains personal context that shouldn't leak
- Write significant events, thoughts, decisions, opinions, lessons learned