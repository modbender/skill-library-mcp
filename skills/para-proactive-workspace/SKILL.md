---
name: para-proactive-workspace
description: "A production-ready workspace template combining PARA Method (Projects, Areas, Resources, Archives) by Tiago Forte with Proactive Agent Architecture for file organization, folder structure, productivity, knowledge management, second brain, and AI agent memory persistence. For OpenClaw. Includes 19+ templates and 3 visual guides."
version: 1.0.0
author: Cocoblood9527
homepage: https://github.com/Cocoblood9527/para-proactive-workspace
---

# PARA + Proactive Agent Workspace 🦞📁

A production-ready workspace template that combines two powerful systems:

1. **PARA Method** (Tiago Forte) - For organizing your content
2. **Proactive Agent Architecture** (Hal Labs) - For AI memory and continuity

## What You Get

### PARA Structure
- `1-projects/` - Active projects with deadlines
- `2-areas/` - Ongoing responsibilities
- `3-resources/` - Reference materials
- `4-archives/` - Completed projects
- `+inbox/` - Temporary inbox (process weekly)
- `+temp/` - Scratch space

### Proactive Agent Memory
- `memory/` - Daily logs and working buffer
- `.learnings/` - Error logs and learnings
- `SESSION-STATE.md` - Active working memory
- `AGENTS.md` - Operating rules
- `SOUL.md` - Agent identity
- `USER.md` - Your profile
- `HEARTBEAT.md` - Periodic checks

## Installation

```bash
# Create workspace directory
mkdir -p ~/workspace
cd ~/workspace

# Copy template files
cp -r ~/.openclaw/skills/para-proactive-workspace/assets/templates/* .

# Or manually create structure following the guide below
```

## Directory Structure

```
workspace/
│
├── 📁 1-projects/          # Active projects
│   └── project-name/
│       ├── README.md
│       ├── notes.md
│       ├── docs/
│       └── assets/
│
├── 📁 2-areas/             # Ongoing responsibilities
│   ├── health/
│   ├── finance/
│   └── learning/
│
├── 📁 3-resources/         # Reference materials
│   ├── articles/
│   ├── books/
│   └── templates/
│
├── 📁 4-archives/          # Completed items
│   └── 2024-projects/
│
├── 📁 +inbox/              # Temporary inbox
├── 📁 +temp/               # Scratch space
│
├── 📁 .agents/             # Agent configuration
├── 📁 .learnings/          # Learning logs
│   ├── ERRORS.md
│   ├── LEARNINGS.md
│   └── FEATURE_REQUESTS.md
│
├── 📁 memory/              # Daily logs
│   └── working-buffer.md
│
├── 📄 AGENTS.md            # Operating rules
├── 📄 HEARTBEAT.md         # Periodic checklist
├── 📄 MEMORY.md            # Long-term memory
├── 📄 ONBOARDING.md        # First-run setup
├── 📄 README.md            # Workspace overview
├── 📄 SESSION-STATE.md     # Active task state
├── 📄 SOUL.md              # Agent identity
├── 📄 TOOLS.md             # Tool configurations
├── 📄 USER.md              # Your profile
└── 📄 .gitignore           # Git ignore rules
```

## PARA Method Explained

### Projects (1-projects/)
**Definition:** A series of tasks linked to a goal, with a deadline.

**Examples:**
- Complete website redesign (due March 1)
- Plan vacation to Japan (departing April 15)
- Launch product feature (Q2 goal)

**When to move to archives:** When completed or cancelled.

### Areas (2-areas/)
**Definition:** A sphere of activity with a standard to be maintained over time.

**Examples:**
- Health & Fitness
- Personal Finance
- Professional Development
- Relationships
- Home Maintenance

**When to move to archives:** When no longer relevant to your life.

### Resources (3-resources/)
**Definition:** A topic or theme of ongoing interest.

**Examples:**
- Gardening tips
- Python programming
- Travel destinations
- Recipes
- Book notes

**When to move to archives:** When no longer interested.

### Archives (4-archives/)
**Definition:** Inactive items from the other three categories.

**Purpose:** Keep out of sight but accessible for reference.

## Proactive Agent Architecture Explained

### Core Files

| File | Purpose | When to Update |
|------|---------|----------------|
| `SOUL.md` | Who the agent is, principles, boundaries | When identity evolves |
| `USER.md` | Who you are, your goals and preferences | As you share more context |
| `AGENTS.md` | Operating rules and workflows | When patterns emerge |
| `TOOLS.md` | Tool configurations and notes | When learning tool usage |
| `SESSION-STATE.md` | Current task and context | Continuously (WAL protocol) |
| `HEARTBEAT.md` | Periodic check checklist | Review regularly |
| `MEMORY.md` | Curated long-term wisdom | Periodically distill |

### Memory System

**Three-tier memory:**
1. **SESSION-STATE.md** - Active working memory (current session)
2. **memory/YYYY-MM-DD.md** - Daily raw logs
3. **MEMORY.md** - Curated long-term wisdom

**WAL Protocol (Write-Ahead Logging):**
- Corrections → Write immediately
- Decisions → Write immediately
- Names/Preferences → Write immediately
- Specific values → Write immediately

**Working Buffer:**
- Activates at 60% context usage
- Captures every exchange
- Survives context compaction

## Usage Workflows

### Daily Workflow
1. **Capture** → Drop files into `+inbox/`
2. **Process** → Sort inbox into PARA folders
3. **Work** → Create/update projects
4. **Log** → Agent writes to `memory/`

### Weekly Review
1. Clear `+inbox/` and `+temp/`
2. Review `2-areas/` for maintenance
3. Archive completed projects
4. Check `.learnings/` for patterns

### Monthly Review
1. Clean `4-archives/`
2. Review `3-resources/` for relevance
3. Update `MEMORY.md` with distilled learnings

## Integration Points

### PARA ↔ Proactive Agent

| PARA | Proactive Agent | Integration |
|------|-----------------|-------------|
| Project notes | `1-projects/X/notes.md` | Agent can read/write |
| Decisions | `SESSION-STATE.md` | WAL protocol captures |
| Daily work | `memory/YYYY-MM-DD.md` | Automatic logging |
| Learnings | `.learnings/LEARNINGS.md` | Error/learning capture |
| Archives | `4-archives/` | Completed projects |

## Best Practices

### For You (Human)
- Process `+inbox/` weekly (Inbox Zero)
- Keep `+temp/` clean daily
- Use consistent naming conventions
- Review areas monthly

### For Your Agent
- Read `SOUL.md` + `USER.md` on startup
- Use WAL protocol for critical details
- Log errors to `.learnings/ERRORS.md`
- Review `HEARTBEAT.md` periodically

## Credits

- **PARA Method:** Tiago Forte (Building a Second Brain)
- **Proactive Agent:** Hal Labs (@halthelobster)
- **Integration:** OpenClaw Community

## License

MIT - Use freely, modify, share.

---

*Organize your content. Empower your agent. Build your second brain.* 🧠🦞
