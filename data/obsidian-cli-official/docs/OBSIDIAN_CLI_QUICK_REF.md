# Obsidian CLI Quick Reference for AI Agents

**For**: Codex, Claude Code, Claude Code, Cursor, Windsurf, and other AI coding assistants

## Prerequisites

```bash
# 1. Check Obsidian is running
pgrep -x "Obsidian" > /dev/null || echo "Start Obsidian first"

# 2. Ensure CLI is in PATH
export PATH="$PATH:/Applications/Obsidian.app/Contents/MacOS"

# 3. Test
obsidian version
```

## Common Commands

### Daily Notes

```bash
# Open today's daily note
obsidian daily

# Add content to today
obsidian daily:append content="## Meeting Notes\n- Item 1\n- Item 2"

# Prepend content
obsidian daily:prepend content="# Important\n\nUrgent task"
```

### Files

```bash
# Create note
obsidian create name="Meeting Notes" content="# Meeting\n\nNotes here"

# Read note
obsidian read file="Meeting Notes"

# Search
obsidian search query="project alpha"

# Delete
obsidian delete file="Old Note"
```

### Tasks

```bash
# List incomplete tasks in daily note
obsidian tasks daily todo

# Toggle task completion (line 3)
obsidian task daily line=3 toggle

# List all tasks
obsidian tasks
```

### Properties (Metadata)

```bash
# Set property
obsidian property:set name="status" value="done" file="Note"

# Read property
obsidian property:get name="status" file="Note"

# Remove property
obsidian property:remove name="status" file="Note"
```

### Tags

```bash
# List all tags with counts
obsidian tags counts

# Sort by count
obsidian tags counts sort=count

# Filter by tag
obsidian search query="tag:#project"
```

### Links

```bash
# Show backlinks
obsidian backlinks file="Note"

# Find orphaned notes
obsidian orphans

# Find unresolved links
obsidian unresolved
```

## Helper Script

For easier usage, use the wrapper script:

```bash
# Install
curl -o ~/bin/obs-helper https://raw.githubusercontent.com/alexanderkinging/obsidian-official-cli/master/scripts/obs-helper.sh
chmod +x ~/bin/obs-helper

# Usage
obs-helper daily
obs-helper daily-add "## Tasks\n- [ ] Review code"
obs-helper note-create "Ideas" "# New Ideas"
obs-helper search "keyword"
obs-helper tasks
```

## Common Patterns

### Morning Routine

```bash
# Create daily note and add tasks
obsidian daily
obsidian daily:append content="## Today's Goals\n- [ ] Review PRs\n- [ ] Write docs"
```

### Meeting Notes

```bash
# Create meeting note with metadata
obsidian create name="Meeting 2026-03-01" content="# Team Sync\n\n## Attendees\n- Alice\n- Bob"
obsidian property:set name="type" value="meeting" file="Meeting 2026-03-01"
obsidian property:set name="date" value="2026-03-01" file="Meeting 2026-03-01"
```

### Project Setup

```bash
# Create project note and link resources
obsidian create name="Project Alpha" content="# Project Alpha\n\n## Overview\n..."
obsidian property:set name="status" value="active" file="Project Alpha"
obsidian bookmark file="Project Alpha.md"
```

## Important Notes

1. **Obsidian must be running** - CLI connects via IPC
2. **Use `file=` for names** - Resolves like wikilinks (no path, no .md)
3. **Use `path=` for exact paths** - Include folder and .md extension
4. **Quote content with spaces** - `content="text with spaces"`
5. **Newlines** - Use `\n` in content strings

## Full Documentation

- **Complete reference**: https://github.com/alexanderkinging/obsidian-official-cli/blob/master/SKILL.md
- **OpenClaw skill**: `clawhub install obsidian-cli-official`
- **Official docs**: https://help.obsidian.md/cli

## Troubleshooting

```bash
# Cannot connect to Obsidian
# → Start Obsidian and enable CLI in Settings → General

# Command not found
# → Add to PATH: export PATH="$PATH:/Applications/Obsidian.app/Contents/MacOS"

# File not found
# → Use file= for name resolution, path= for exact paths
```

---

**Version**: 3.1.0  
**Author**: alexanderkinging  
**License**: MIT
