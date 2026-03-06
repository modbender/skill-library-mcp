# Kickstart Setup Guide

Follow these steps in order. Each one builds on the last.

---

## Step 1: Know Your Workspace

Your workspace is at `~/.openclaw/workspace/` (or wherever your OpenClaw instance points). This is home — every file you create lives here.

Check what exists:
```bash
ls -la ~/.openclaw/workspace/
```

If you see AGENTS.md, SOUL.md etc already, you have an existing setup. This guide will upgrade it. If it's empty, you're starting fresh.

---

## Step 2: Install Core Files

Copy the template files from this skill into your workspace. Read each one and customise before using.

### AGENTS.md (Agent Operating Manual)

Copy `assets/AGENTS.md` to your workspace root. This controls:
- How your agent reads files on startup
- Memory protocols (what to write down, where)
- Safety boundaries (what to do freely vs ask first)
- Group chat behaviour (when to speak, when to stay silent)
- Sub-agent spawning rules (Context Bundle Protocol)
- Heartbeat behaviour (proactive checks)

**Customise:** Read through it and adjust boundaries to your comfort level. The defaults are conservative — you can loosen them as trust builds.

### SOUL.md (Personality)

Copy `assets/SOUL.md` to your workspace root. This defines your agent's voice and personality.

**Customise:** This is the most personal file. Change the tone, boundaries, and vibe to match what you want. Some people want formal, some want casual. Make it yours.

### anchor.md (Compaction Safety Net)

Copy `assets/anchor.md` to your workspace root. This is a small file (~300-500 tokens) with your absolute non-negotiable rules. It exists because context compaction can silently remove instructions from your agent's working memory mid-session. Your agent re-reads this before any risky action.

**Customise:** Fill in your agent name, your name, your voice preference, and your specific constraints. See `references/compaction-survival.md` for the full guide on why this matters and 5 more techniques.

### HEARTBEAT.md (Proactive Checks)

Copy `assets/HEARTBEAT.md` to your workspace root. This tells your agent what to check during heartbeat polls.

**Customise:** Add checks relevant to your setup — email, calendar, weather, project status, whatever matters to you.

---

## Step 3: Set Up Memory Architecture

Create the memory directory:
```bash
mkdir -p ~/.openclaw/workspace/memory
```

### Daily Notes Pattern
Your agent creates `memory/YYYY-MM-DD.md` files automatically as things happen. These are raw logs — decisions, events, context. No need to create these manually.

### MEMORY.md (Long-Term Memory)
Create an empty `MEMORY.md` in your workspace root:
```bash
touch ~/.openclaw/workspace/MEMORY.md
```

This is your agent's curated long-term memory. Over time, your agent reviews daily files and distils the important stuff here. Think of daily files as a journal, MEMORY.md as wisdom.

### Heartbeat State Tracker
Create the rotation tracker:
```bash
echo '{"lastChecks": {}}' > ~/.openclaw/workspace/memory/heartbeat-state.json
```

This tracks when each type of check was last run, preventing duplicate checks.

### Memory Maintenance
Your agent should periodically (every few days) review recent daily files and update MEMORY.md. Add this to AGENTS.md if not already there. Old daily files can be archived or deleted after their insights are captured.

---

## Step 4: Install References

Copy the references folder from this skill:

### Soul Library (`references/soul-library.md`)
Expert personas for common task types. Your agent prepends these when spawning sub-agents or tackling specific task types.

### Context Bundle Protocol (`references/context-bundle-protocol.md`)
Template for spawning sub-agents with full context. Eliminates the cold-start problem where sub-agents guess at your goals and produce off-target results.

**Key rule:** Every spawned task MUST include a verification step.

---

## Step 5: Create Identity Files

These files you fill in yourself:

### USER.md
```markdown
# USER.md - About Your Human
- **Name:** [Your name]
- **What to call them:** [Preferred name]
- **Location:** [City, Country]
- **Timezone:** [e.g., Europe/London]
- **Notes:** [Anything your agent should know about you]
```

### IDENTITY.md
```markdown
# IDENTITY.md
- **Name:** [Your agent's name]
- **Creature:** [What kind of entity — AI assistant, digital companion, etc]
- **Vibe:** [Personality in a few words]
- **Emoji:** [Signature emoji]
```

---

## Step 6: Configure Heartbeats

In your OpenClaw config (`openclaw.json` or via gateway), set up heartbeat polling:

```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "intervalMinutes": 30,
        "activeHours": { "start": 8, "end": 23 },
        "timezone": "Europe/London"
      }
    }
  }
}
```

Adjust the interval and hours to your preference. Your agent will check HEARTBEAT.md at each interval and either act on what it finds or reply HEARTBEAT_OK.

---

## Step 7: Configure Your Models

See `references/model-strategy.md` for the full breakdown. The short version:

- **Setup/onboarding:** Use Opus (worth the one-time cost)
- **Daily use:** Switch to Sonnet or a cheaper model
- **Heartbeats:** Use Haiku — this alone saves 80%+ on background costs
- **Configure fallbacks** so your agent doesn't break if a model is rate-limited

Most people overspend 3-5x because they never change the default model.

---

## Step 8: Set Up Your First Automation

See `references/automation-patterns.md` for templates. Start simple:

1. **Morning briefing** — Daily summary cron at your preferred time
2. **Heartbeat rotation** — Cycle through email, calendar, weather checks
3. **Memory maintenance** — Periodic review and MEMORY.md updates

Don't try to automate everything at once. Add one automation, get it stable, then add the next.

---

## Step 9: Install Companion Skills

These optional skills work great alongside Kickstart:

```
npx clawhub install qmd
npx clawhub install github
```

- **qmd** — Local search across all your memory files. Instead of loading entire files into context, your agent searches and pulls only what's relevant. The single biggest upgrade for memory management.
- **github** — GitHub CLI integration for managing repos, issues, PRs from your agent.

Also worth considering: google-calendar, weather.

---

## Step 10: Grab Your APIs

See `references/api-checklist.md` for which free APIs to set up and in what order.

---

## Step 10: Read Next Steps

See `references/next-steps.md` for how to grow from here — channel skills, project skills, and scaling your agent's capabilities.

---

## Troubleshooting

**Agent not reading files on startup:** Check AGENTS.md is in the workspace root and contains clear "Every Session" instructions.

**Memory getting too large:** Implement the pruning strategy from `references/memory-architecture.md`. Daily files older than 2 weeks with insights captured in MEMORY.md can be archived.

**Sub-agents producing bad results:** Use the Context Bundle Protocol. Pack full context, constraints, and verification steps into every spawn.

**Heartbeat too noisy:** Reduce check frequency or narrow the active hours. Add explicit "stay quiet" rules to HEARTBEAT.md for off-hours.

**Context window filling up:** Keep MEMORY.md under 500 lines. Archive old daily files. Use progressive disclosure — don't load everything every session.
