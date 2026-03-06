---
name: Capability Awareness System
description: Makes OpenClaw agents aware of custom skills and capabilities.
  Skills-first approach with on-demand documentation loading. Zero overhead when
  not in use. Foundation for skill marketplace discovery.
---

# Capability Awareness System

Makes OpenClaw agents aware of custom skills and capabilities. Skills-first approach with on-demand documentation loading. Zero overhead when not in use. Foundation for skill marketplace discovery.

**When to use:** Skill discovery, capability documentation, agent self-awareness of available tools

**What to know:**

**Repository:** https://github.com/pfaria32/openclaw-capability-awareness

## Problem

Default OpenClaw agents don't know about custom skills you've installed. They need to:
1. Discover what capabilities exist
2. Know when to use each skill
3. Access skill documentation on demand

## Solution

**Skills-First Approach:**
- Agent sees skill descriptions in prompt
- Reads full SKILL.md when topic is relevant
- Zero overhead when skills not in use
- Simple, proven, low-risk

## Implementation Options

### Option 1: Skills-First (Recommended for v1)
Add capability cards to agent prompt:
```
Available Skills:
- token-economy: Model routing and cost optimization
- health-tracking: Apple Health and Strava integration
- memory-system: RAG-based semantic search
```

Agent reads full SKILL.md when needed.

### Option 2: Full Injection (Advanced)
- Router-gated skill loading
- Dynamic prompt injection
- Context-aware capability exposure
- Zero baseline cost (only loads when relevant)

## Installation

```bash
cd /home/node/.openclaw/workspace
git clone https://github.com/pfaria32/openclaw-capability-awareness.git projects/capability-awareness-system
```

## Usage

### Current Implementation (Skills-First)
Skills are documented in `workspace/skills/*/SKILL.md`. The agent loads these automatically through the AGENTS.md workflow:

```markdown
## Skills (mandatory)
Before replying: scan <available_skills> <description> entries.
- If exactly one skill clearly applies: read its SKILL.md at <location> with `read`, then follow it.
```

This is already working! Just add new skills to the workspace/skills directory.

### Future Implementation (Full Injection)
See repository for:
- Router design and schema
- Embedding-based skill matching
- Dynamic prompt injection strategy
- Cost/token analysis

## Status

✅ **Skills-First approach** — Deployed and working
📋 **Full Injection design** — Documented, not yet implemented

## Attribution

Built to support the emerging OpenClaw skill ecosystem. Simple beats clever.

## Documentation

Implementation options, design decisions, and upgrade path documented in repository.
