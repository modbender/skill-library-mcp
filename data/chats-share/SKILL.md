---
name: chats-share
description: "Use when user wants to share OpenClaw channel conversations externally"
metadata: {"openclaw":{"emoji":"💬","homepage":"https://github.com/imyelo/openclaw-chats-share"}}
---

# chats-share

Share OpenClaw conversations as public web pages.

## When to Use

- User wants to share a conversation externally
- User wants to export conversation history for docs

## Config

**Project dir**: Where `create-openclaw-chats-share` was run

- **OpenClaw**: Read from `~/.openclaw/workspace/TOOLS.md`
- **Other agents**: Pass as argument

**site**: Read `site` URL from `{projectDir}/chats-share.toml`

**outputDir**: `{projectDir}/chats/` (convention, not config)

## Steps

1. **Pre-check**: Check if a `chats-share` project dir is configured in TOOLS.md
   - Read `~/.openclaw/workspace/TOOLS.md`
   - If no project directory found → Run first-time setup (see "First Time Setup" section below)
2. Load project dir (from TOOLS.md or arguments)
3. Load `site` URL from `{projectDir}/chats-share.toml` (use as base for output URL)
4. Find session:
   - List all sessions: `ls -t ~/.openclaw/agents/main/sessions/*.jsonl`
   - Filter by:
     - `sessionId=xxx` → grep exact ID
     - `topic=xxx` → grep topic keyword in content
     - `current` → use most recent (first line after ls -t)
   - Show candidates to user for confirmation
5. Parse to temp: `openclaw-chats-share parse {session} -o {projectDir}/chats/.tmp/{timestamp}.md`
6. Digest summary from parsed file, suggest topic name based on content (e.g. "How to use OpenClaw with Python")
7. Confirm participants: Read the auto-generated `participants` frontmatter from the temp file.
   Show the current entries and ask the user if they want to customize the display names
   (e.g. rename `user` to their real name, or `assistant` to the agent's display name).
   Update the frontmatter in-place if the user provides new names — keep all other fields (`role`, `model`) unchanged.
8. Confirm with user: show preview, ask to confirm or modify topic name
9. Rename: `mv {temp} {projectDir}/chats/{YYYYMMDD}-{topic}.md`
10. Redact sensitive info (e.g.: API keys, tokens, paths, emails, IPs) (see "Redact" section below)
11. Confirm with user before commit: `git add {projectDir}/chats/{topic}.md && git commit -m "docs: add {topic}"`
12. Confirm with user before push: `git push`

## First Time Setup

Run once to initialize project:
```bash
create-openclaw-chats-share
```
This sets up the project structure.

After setup, register project in TOOLS.md:
```bash
# Append to ~/.openclaw/workspace/TOOLS.md
echo -e "\n## chats-share\n\n- Project: {projectDir}\n" >> ~/.openclaw/workspace/TOOLS.md
```

## Redact

When sharing publicly, review and redact:
- API keys, tokens, passwords
- File paths with usernames (`/Users/xxx` → `~`)
- Email addresses, phone numbers
- Internal URLs and private IPs

## Output

- File: `{projectDir}/chats/{YYYYMMDD}-{topic}.md`
- URL: `{site}/share/{slug}`

## Dev

Run local dev server:
```bash
openclaw-chats-share-web dev
```
