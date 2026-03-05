---
name: conversation-archiver
description: Archive completed conversations and projects. Use on project completion, resolved threads, or when asked to archive a conversation. Writes structured summaries to files and optionally posts to a Discord channel.
---

# Conversation Archiver

Standardized workflow for archiving completed conversations and projects.

## Requirements

- File system access (workspace directory)
- Optional: OpenClaw Discord channel for posting summaries

## When to Use

- Project reaches completion
- A conversation thread is resolved
- User says "archive this" or "we're done with X"
- Periodic cleanup of old project channels

## Workflow

1. **Write summary file**:
   - Path: `archive/conversations/YYYY-MM-DD_topic-slug.md`
   - Format:
     ```markdown
     # [Topic Name]
     **Date:** YYYY-MM-DD
     **Duration:** [how long the project/conversation spanned]
     **Status:** Completed

     ## Summary
     [2-3 paragraph summary of what happened]

     ## Key Decisions
     - [Decision 1]
     - [Decision 2]

     ## Outcomes
     - [What was built/changed/resolved]

     ## Open Items
     - [Anything left unresolved, or "None"]
     ```

2. **Post to Discord** (optional): Send summary to a designated archive channel
   - Keep Discord post concise -- summary + outcomes only
   - Link to the full file if details are long

3. **Update daily memory**: Add a line to today's memory file noting the archival

4. **Update tasks**: If the conversation relates to a tracked task, mark it complete

## Naming Convention

File slug: lowercase, hyphens, no special chars. Examples:
- `2026-02-24_discord-server-cleanup.md`
- `2026-02-20_multi-user-agent-deploy.md`
- `2026-02-15_connector-setup.md`

## Configuration

Set these in your workspace to customize:
- **Archive directory**: Default `archive/conversations/` relative to workspace
- **Discord channel**: Set a channel ID for posting summaries (optional)
- **Memory file pattern**: Default `memory/YYYY-MM-DD.md`
