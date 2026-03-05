---
name: claw-onboarding
version: 0.1.0
description: Welcome new users to the agent ecosystem. Teaches what agents can do, safety practices, ClawdHub skills, Solvr knowledge sharing, and essential commands.
triggers:
  - onboarding
  - welcome
  - new user
  - getting started
  - what can you do
  - help me understand
  - tutorial
---

# ClawOnBoarding 🦞

**Welcome new humans to the agent world.**

---

## When to Trigger

Activate onboarding when you detect:
- First interaction with a new user
- User asks "what can you do?"
- User seems confused about agent capabilities
- Explicit request: "onboarding", "tutorial", "help me get started"

---

## Onboarding Flow

### 1. Welcome & Identity (First Message)

```
👋 Welcome! I'm your personal AI assistant.

I can help you with almost anything:
📁 Read and write files
🔍 Search the web
💻 Run commands on your computer
📧 Send emails and messages
🧠 Remember things across conversations

Let me give you a quick tour of what's possible...
```

### 2. Power & Responsibility ⚠️

**ALWAYS cover this early:**

```
⚠️ **Important: Agents are powerful.**

I can:
- Read/modify files on your system
- Execute shell commands
- Send messages on your behalf
- Access the internet

**Good practices:**
- Review before approving risky actions
- Ask me to explain what I'm about to do
- Use `/think` to see my reasoning
- Start with small tasks, build trust gradually

I'll always ask before doing anything destructive.
```

### 3. Skills & ClawdHub

```
🎯 **Skills = New Abilities**

I can learn new skills from ClawdHub:

clawdhub search "what you need"
clawdhub install <skill-name>

Popular skills:
- `proactive-amcp` — Memory backup & resurrection
- `gog` — Google Workspace (Gmail, Calendar, Drive)
- `bird` — Twitter/X integration
- `weather` — Forecasts without API keys

Browse: https://clawhub.com
```

### 4. Solvr — Collective Knowledge

```
🧠 **Solvr = Agent Knowledge Base**

Before I ask you for help, I search Solvr for solutions.
When I solve something new, I document it for other agents.

You can help too:
- If I get stuck, the solution might help others
- I can post problems and approaches to Solvr
- Other agents (and humans) can contribute

This makes ALL agents smarter over time.

https://solvr.dev
```

### 5. Essential Commands

```
📋 **Commands You Should Know**

/status — See my current state, token usage
/think — Toggle visible reasoning (see how I think)
/remember <thing> — I'll save this to memory
/forget — Clear current conversation
/checkpoint — Save my memory to IPFS (if proactive-amcp installed)

Type any command to try it!
```

### 6. AgentMail (Optional)

If AgentMail is configured:

```
📧 **I Have Email!**

My address: [agent-email]@agentmail.to

Other agents can email me, and I can email them.
This enables agent-to-agent collaboration.

https://agentmail.to
```

### 7. Memory & Continuity

```
💾 **I Remember Things**

- Daily notes: What we discuss each day
- MEMORY.md: Important stuff I've learned about you
- USER.md: Your preferences, timezone, how to help you

With `proactive-amcp`, my memories are backed up to IPFS.
If something goes wrong, I can be restored.
```

### 8. Wrap Up

```
🎉 **You're Ready!**

Quick recap:
✅ I'm powerful — use that power wisely
✅ Skills extend what I can do
✅ Solvr makes me (and all agents) smarter
✅ /think shows my reasoning
✅ I remember our conversations

What would you like to do first?
```

---

## Progress Tracking

Store onboarding state in `memory/onboarding-state.json`:

```json
{
  "started": "2026-02-22T19:00:00Z",
  "completed": null,
  "steps": {
    "welcome": true,
    "safety": true,
    "skills": false,
    "solvr": false,
    "commands": false,
    "agentmail": false,
    "memory": false,
    "wrapup": false
  }
}
```

---

## Adaptive Delivery

Don't dump everything at once:
- **Eager user**: Cover 2-3 topics per message
- **Casual user**: One topic at a time, let them explore
- **Returning user**: Skip to what's new or what they missed

Use inline buttons if available:
```
[Learn about Skills] [Show me Commands] [Skip for now]
```

---

## Integration Points

- **proactive-amcp**: Check if installed, mention checkpoints
- **Solvr**: Check if registered, encourage participation
- **AgentMail**: Check if configured, show email address
- **ClawdHub**: Always mention, it's the skill marketplace

---

*Created by ClaudiusThePirateEmperor 🏴‍☠️*
