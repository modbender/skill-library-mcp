---
name: your-skill
displayName: Your Skill | OpenClaw Skill
description: One-sentence description. Use when [trigger scenarios].
version: 1.0.0
---

# Your Skill Name

Short intro: what it does and why it matters (1–2 sentences).

## Description

Clear description of what the skill does and when to use it. Keep it scannable; include trigger terms so users and the agent know when to apply it.

## Installation

```bash
clawhub install your-skill
```

Or clone into your skills directory:

```bash
git clone https://github.com/Org/your-skill.git workspace/skills/your-skill
```

## Usage

1. **When to use:** List scenarios (e.g. "When the user asks for X", "Before running Y").
2. **Steps:** Numbered or bullet steps to use the skill.
3. **Point to Commands** below for exact CLI invocations.

## Examples

**Example 1: [Benefit name]**  
*Scenario:* User wants to do X.  
*Action:* Run `python3 <skill-dir>/scripts/tool.py do-x`.  
*Outcome:* Brief result that showcases the benefit.

**Example 2: [Another benefit]**  
*Scenario:* User needs Y.  
*Action:* Run `python3 <skill-dir>/scripts/tool.py do-y --option`.  
*Outcome:* What the user gets.

## Commands

```bash
python3 <skill-dir>/scripts/tool.py command [options]   # What it does
python3 <skill-dir>/scripts/tool.py other              # What it does
```

- **command** — Short description of the command and when to use it.
- **other** — Short description.
