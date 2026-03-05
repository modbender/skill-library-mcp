---
name: memory-manager
description: Automatic session logging and memory management for infrastructure, projects, and tools. Use at the end of sessions containing changes to servers, services, deployments, cron jobs, repositories, APIs, integrations, or credentials. Ensures consistent documentation without context bloat.
---

# Memory Manager

Intelligent session-end memory management. Automatically captures important infrastructure, project, and tool changes while filtering out noise.

## When This Skill Triggers

Run at session end when the conversation included:
- **Infrastructure**: server, deploy, service, systemd, nginx, docker, database
- **Projects**: repository, github, feature, cron, API endpoint
- **Tools**: integration, credential, API key, configuration

## What Gets Saved

### Daily Log (ALWAYS)
File: `memory/YYYY-MM-DD.md`

**Save:**
- New/changed services or servers
- Project deployments or major features
- Cron job updates
- Infrastructure fixes or migrations
- Important bugs and their solutions
- Configuration changes

**Skip:**
- Chat conversation
- Debugging steps (unless they reveal important lessons)
- Temporary tests
- Minor code tweaks

### MEMORY.md (ONLY structural changes)
**Save:**
- New projects (with basic info)
- Changed workflows or architecture
- Important design decisions
- Deprecated/archived systems

**Skip:**
- Routine updates
- Temporary changes
- Details already in daily logs

### TOOLS.md (ONLY new tools/credentials)
**Save:**
- New API keys or credentials
- New servers (IP, SSH, purpose)
- New integrations

### PROJECTS.md (Project lifecycle changes)
See references/projects-guide.md for full schema.

**Save:**
- New projects started
- Status changes (Prototype → Production, Active → Archived)
- Major tech stack changes
- URL or deployment location changes

## Process

1. **Scan session** for infrastructure/project/tool keywords
2. **Filter** using criteria above
3. **Write daily log** with timestamp + structured summary
4. **Update MEMORY.md** only if structural change
5. **Update TOOLS.md** only if new credential/server/integration
6. **Update PROJECTS.md** only if project lifecycle change

## Daily Log Format

```markdown
## HH:MM UTC — Brief Title

**What happened:** 1-2 sentence summary

**Changes:**
- Service X deployed to server Y
- Cron job Z updated with new logic
- Project A: feature B shipped

**Impact:** (only if significant)
- Performance improved 2x
- Fixed critical bug affecting users
```

## MEMORY.md Update Guidance

Only add if it's something you need to remember **long-term** across sessions:
- New permanent services
- Architectural decisions
- Deprecated patterns

Keep entries **under 5 lines**. Details go in daily logs.

## References

- [PROJECTS.md Guide](references/projects-guide.md) - Schema and update criteria
