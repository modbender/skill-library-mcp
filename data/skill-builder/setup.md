# Setup — Skill Builder / Creator

Reference this file when helping users create skills.

## Your Role

Help users create effective skills. Guide them through structure, naming, and best practices.

## Priority Order

### 1. Understand the Goal

Ask:
- "What should this skill help with?"
- "What tasks will it handle?"

Listen for: domain, triggers, audience (human using agent vs agent-to-agent).

### 2. Identify the Structure

Based on their goal, determine:
- Does it need memory? (tracks preferences, history, state)
- Does it call external APIs?
- Does it need scripts for deterministic tasks?
- How much auxiliary content?

### 3. Guide the Build

Walk them through:
1. Name and description (critical for discovery)
2. Core Rules (what the agent MUST do)
3. Traps (where models fail)
4. File structure

## Key Principles to Convey

**Concise over comprehensive:**
"Models are smart. Only add what they don't already know."

**Progressive disclosure:**
"Details go in separate files, loaded when needed."

**Description matters most:**
"This is what agents read to decide if your skill matches their query."

## When Done

You're ready when:
- Clear understanding of what the skill does
- Draft structure outlined
- User knows what files they need

Everything else builds iteratively.
