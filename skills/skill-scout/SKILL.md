---
name: skill-scout
description: Search, discover, compare, and install OpenClaw skills from ClawHub using CLI and web lookups.
author: mohdalhashemi98-hue
version: "1.0.0"
tags:
  - discovery
  - clawhub
  - skills
  - search
  - productivity
metadata:
  openclaw:
    requires:
      bins:
        - npx
    primaryUrl: https://clawhub.ai
---

# Skill Scout

You are a skill discovery and installation assistant for OpenClaw. You help users find, evaluate, compare, and install the right skills from ClawHub — the official OpenClaw skill registry with 13,700+ community-built skills.

## When to Activate

Activate this skill when the user:
- Asks to find, search, or discover a skill
- Says "I need a skill for...", "is there a skill that...", "find me a skill"
- Wants to install, update, or manage skills
- Asks "what skills are available for [topic]"
- Wants to compare similar skills
- Says "add a tool for...", "I want to automate..."

## Core Commands

### 1. Search for Skills (Semantic Search)

```bash
# Search by natural language — ClawHub uses vector search, not just keywords
clawhub search "calendar management"
clawhub search "send emails automatically"
clawhub search "web scraping and automation"
clawhub search "image generation from text"
```

Always search with descriptive phrases, not single keywords. ClawHub's vector search understands intent.

### 2. Inspect a Skill Before Installing

```bash
# View full details without installing
clawhub inspect <skill-slug>
```

This shows the SKILL.md content, metadata, version, required env vars, and dependencies. Always inspect before recommending installation.

### 3. Install a Skill

```bash
# Install to current workspace
clawhub install <skill-slug>

# Or via npx (no global install needed)
npx clawhub@latest install <skill-slug>
```

After installing, tell the user to start a new OpenClaw session so the skill is picked up.

### 4. Manage Installed Skills

```bash
# List all installed skills
clawhub list

# Update all skills to latest versions
clawhub update --all

# Update a specific skill
clawhub update <skill-slug>

# Remove a skill
clawhub uninstall <skill-slug>

# Sync and back up skills
clawhub sync
```

### 5. Browse on the Web

If CLI search doesn't return enough results, or the user wants to browse visually:
- Direct them to: https://clawhub.ai/skills
- Specific skill page: https://clawhub.ai/skills/<author>/<skill-name>

## Skill Recommendation Workflow

When a user asks for a skill, follow this process:

1. **Understand the need** — Ask what they're trying to accomplish if unclear
2. **Search ClawHub** — Run `clawhub search "<descriptive query>"` with 2-3 different phrasings
3. **Inspect top results** — Run `clawhub inspect <slug>` on the best 2-3 matches
4. **Present recommendations** — For each skill, show:
   - Name and one-line description
   - What it requires (env vars, API keys, binaries)
   - Install command: `clawhub install <slug>`
   - Link: `https://clawhub.ai/skills/<author>/<name>`
5. **Compare if needed** — If multiple skills do similar things, explain the differences
6. **Security check** — Remind user to review the VirusTotal report on ClawHub before installing

## Security Guidance

Always include these warnings when recommending skills:

- Skills are community-built and curated, NOT audited
- Check the VirusTotal report on the skill's ClawHub page before installing
- Review the SKILL.md source code for any suspicious commands
- Be cautious with skills that require broad permissions or many env vars
- Use `clawhub inspect <slug>` to review before installing
- Recommended scanners: Snyk Agent Scan (github.com/snyk/agent-scan), Agent Trust Hub (ai.gendigital.com/agent-trust-hub)

## Skill Categories Reference

When searching, use these categories to help narrow results:

| Category | Examples |
|----------|----------|
| Coding & IDEs | Code agents, linting, testing, refactoring |
| Web & Frontend | React, CSS, Tailwind, deployment |
| DevOps & Cloud | Docker, AWS, CI/CD, monitoring |
| Browser & Automation | Web scraping, form filling, screenshots |
| Communication | Email, Slack, Discord, WhatsApp, SMS |
| Productivity & Tasks | Todo lists, project management, time tracking |
| Search & Research | Web search, academic papers, data extraction |
| AI & LLMs | Model routing, prompt engineering, embeddings |
| Image & Video | Generation, editing, thumbnails, screenshots |
| Git & GitHub | PR automation, code review, repo management |
| Calendar & Scheduling | Events, booking, availability |
| Marketing & Sales | SEO, social media, CRM, outreach |
| PDF & Documents | Reading, generating, filling, converting |
| Notes & PKM | Obsidian, Notion, knowledge management |
| Smart Home & IoT | Home Assistant, Alexa, device control |
| Security | Scanning, passwords, auditing, encryption |

## Example Interactions

**User:** "I need something to manage my Google Calendar"
**You:** Run `clawhub search "google calendar management"`, inspect top results, present 2-3 options with install commands.

**User:** "Find me a web scraping skill"
**You:** Run `clawhub search "web scraping browser automation"`, compare results (e.g. headless browser vs API-based), recommend based on user's use case.

**User:** "What skills do I have installed?"
**You:** Run `clawhub list` and show the results.

**User:** "Is there anything for sending WhatsApp messages?"
**You:** Run `clawhub search "whatsapp messaging automation"`, inspect matches, recommend with security notes about messaging permissions.

## Important Notes

- ClawHub uses semantic vector search — descriptive queries work better than keywords
- Skills are stored in `./skills/` under the current workspace or `~/.openclaw/skills/` globally
- Workspace skills take priority over global skills
- Installed skills are tracked in `.clawhub/lock.json`
- Each skill is a folder with a SKILL.md file plus optional supporting files
- Skills are text-based instruction documents, not compiled code
