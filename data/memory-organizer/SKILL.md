---
name: memory-organizer
description: Organize and compress memory files to reduce context loading in new sessions. Automatically identify important information and discard redundant content.
metadata:
  {
    "openclaw": { "emoji": "🧠" }
  }
---

# Memory Organizer Skill

Tool for organizing and compressing memory files.

## Features

1. **Scan memory files** - View all memories in memory/ directory
2. **Analyze content** - Identify important info (user preferences, project config, todos)
3. **Compress & organize** - Summarize lengthy content, keep core info
4. **Clean up** - Delete outdated or unnecessary content

## Use Cases

- Memory files too large, slow to load each session
- Want to extract key info, discard details
- Need regular memory maintenance

## Commands

### Scan memories

```bash
memory-organizer scan
```

### Classify by topic

```bash
memory-organizer classify
```

### Find redundant memories

```bash
memory-organizer redundant
```

### Discard redundant memories

```bash
memory-organizer discard redundant --force
```

### Compress a memory file

```bash
memory-organizer compress 2026-01-01.md        # Keep titles and key lines
memory-organizer compress 2026-01-01.md --titles  # Keep titles only
memory-organizer compress 2026-01-01.md --aggressive  # Aggressive compression
```

### Merge to main memory

```bash
memory-organizer merge 2026-01-01.md
```

### View memory content

```bash
memory-organizer view 2026-01-01.md
```

### Cleanup backups

```bash
memory-organizer clean
```

## Topic Classification

The organizer automatically classifies memories into:

- **用户偏好 (User Preferences)** - name, timezone, preferences
- **项目配置 (Project Config)** - agents, cron jobs, workspaces
- **技能 (Skills)** - installed skills, tools
- **赚钱点子 (Money Ideas)** - side hustle ideas, projects
- **待办事项 (Todos)** - tasks, plans, next steps
- **技术记录 (Tech Notes)** - code, commands, solutions
- **日常 (Daily)** - daily logs, routine

## Best Practices

1. Run organization daily or weekly
2. Keep key info: user preferences, project config, todos
3. Discard details: logs, temporary thoughts
4. Keep MEMORY.md concise (< 100 lines)

## Recommended File Structure

```
# User Preferences
- Name, how to address
- Timezone
- Key preferences

# Project Config
- Agent configurations
- Scheduled tasks
- Important file paths

# Todos
- Current tasks
- Next steps
```
