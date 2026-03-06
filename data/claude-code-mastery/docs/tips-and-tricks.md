# Claude Code Tips & Tricks

A curated collection of pro tips from heavy users and the community.

## Context Management

### Tip 1: AI Context is Like Milk
Fresh and condensed is best. Claude performs best at the start of conversations. As context fills, performance degrades.

**Action:** Start new conversations for new topics. Don't let unrelated context accumulate.

### Tip 2: Proactive Compaction with HANDOFF.md
Instead of relying on auto-compact, create handoff documents:

```
Put the rest of the plan in HANDOFF.md. Explain:
- What you tried
- What worked, what didn't
- Next steps

So the next agent with fresh context can continue.
```

Then start fresh: `> HANDOFF.md`

### Tip 3: /clear is Your Friend
Use `/clear` liberally:
- Between unrelated tasks
- After two failed correction attempts
- When performance seems degraded

### Tip 4: Subagents for Exploration
Don't pollute your main context with exploration. Use subagents:

```
Use a subagent to investigate how authentication handles token refresh,
and whether we have existing OAuth utilities to reuse.
```

The subagent explores in its own context and reports back a summary.

## Workflow Optimization

### Tip 5: Voice Transcription
Speaking is faster than typing. Local transcription tools work well:
- superwhisper (Mac)
- MacWhisper
- Whisper-based tools

Even with transcription errors, Claude understands intent.

### Tip 6: Terminal Aliases
```bash
alias c='claude'
alias ch='claude --chrome'
alias q='cd ~/projects'
```

Combine with flags: `c -c` to continue, `c -r` to resume.

### Tip 7: Markdown Everything
Write in markdown files. Claude Code + markdown = efficient writing workflow.

**Tip:** To paste markdown into platforms that don't accept it, paste into Notion first, then copy from Notion.

### Tip 8: Cmd+A/Ctrl+A for Context
When Claude can't access a URL, select all visible content (Cmd+A), copy, paste directly into Claude Code.

Works for:
- Private pages
- Sites that block bots
- Terminal output
- Email threads (use "Print All" for Gmail)

## Git Mastery

### Tip 9: Draft PRs
Let Claude create draft PRs—low risk, review before marking ready:

```
create a draft PR for these changes with detailed description
```

### Tip 10: Allow Pull, Supervise Push
Configure permissions to allow pull automatically but require approval for push. Safer workflow.

### Tip 11: Git Worktrees for Parallel Work
```
create a git worktree for feature/new-auth in ../feature-branch
```

Work on multiple branches simultaneously without conflicts.

### Tip 12: GitHub CLI Power
Claude can use `gh` for complex operations:
```
use gh to find when this PR description was last edited
```

## Session Management

### Tip 13: Name Your Sessions
```
/rename oauth-migration
```

Find them later with `claude -r`.

### Tip 14: Session Picker Shortcuts
In `/resume` picker:
- `↑/↓` Navigate
- `→/←` Expand/collapse grouped sessions
- `P` Preview
- `R` Rename
- `B` Filter to current branch
- `A` Toggle all projects

### Tip 15: Cascade Method for Multitasking
- Open new tab for each task (right side)
- Sweep left to right, oldest to newest
- Keep to 3-4 active tasks max

## Verification Strategies

### Tip 16: Complete the Write-Test Cycle
For autonomous tasks, give Claude a way to verify:
- Write code → Run it → Check output → Repeat

For interactive testing, use tmux:
```bash
tmux new-session -d -s test-session
tmux send-keys -t test-session 'command' Enter
sleep 2
tmux capture-pane -t test-session -p
```

### Tip 17: Playwright vs Native Chrome
- **Playwright MCP:** Better for most tasks, uses accessibility tree
- **Native Chrome (`/chrome`):** Better for logged-in state, visual testing

Put in CLAUDE.md:
```markdown
# Claude for Chrome
- Use `read_page` for element refs from accessibility tree
- Use `find` to locate elements by description
- Click using `ref`, not coordinates
- NEVER take screenshots unless explicitly requested
```

### Tip 18: Manual Exponential Backoff
For long-running jobs (CI, Docker builds):
```
check status with increasing intervals: 1 min, then 2 min, then 4 min
let me know when it's done
```

More token-efficient than continuous polling.

## Output & Integration

### Tip 19: Getting Output Out
- **Clipboard:** Ask Claude to use `pbcopy`
- **File:** Write to file, open in VS Code
- **URL:** Ask Claude to open in browser
- **GitHub Desktop:** Ask to open current repo

### Tip 20: Pipe In, Pipe Out
```bash
# Pipe data through Claude
cat error.log | claude -p 'explain root cause' > analysis.txt

# Use as linter
claude -p 'check for issues vs main' --output-format json
```

## Advanced Techniques

### Tip 21: Slim the System Prompt
Claude Code's system prompt uses ~19k tokens. Can be reduced to ~9k with patching. See [ykdojo/claude-code-tips](https://github.com/ykdojo/claude-code-tips) for patches.

**Note:** Requires npm installation, disable auto-updates:
```json
{
  "env": {
    "DISABLE_AUTOUPDATER": "1"
  }
}
```

### Tip 22: Lazy-Load MCP Tools
Add to `~/.claude/settings.json`:
```json
{
  "env": {
    "ENABLE_TOOL_SEARCH": "true"
  }
}
```

Tools load on-demand instead of filling context upfront.

### Tip 23: Custom Status Line
Customize the status bar to show model, token usage, git status. See community scripts.

### Tip 24: Search Conversation History
Conversations stored in `~/.claude/projects/`

```bash
# Find conversations mentioning "auth"
grep -l -i "auth" ~/.claude/projects/*/*.jsonl

# Today's conversations
find ~/.claude/projects/*/*.jsonl -mtime 0 -exec grep -l -i "keyword" {} \;
```

### Tip 25: Use Gemini as Fallback
For sites Claude can't access (Reddit), create a skill that uses Gemini CLI:

```markdown
# ~/.claude/skills/reddit-fetch/SKILL.md
When WebFetch can't access Reddit, use Gemini CLI as fallback
with tmux to capture output.
```

## Prompting Tips

### Tip 26: Ask for Boring Solutions
```
give me a boring, conventional solution
optimize for readability by mid-level engineers
```

Reduces unnecessary complexity.

### Tip 27: Diff-First Approach
```
show changes as a unified diff
```

Easier to track modifications.

### Tip 28: Let Claude Interview You
```
Interview me about [feature] in detail.
Ask about technical implementation, edge cases, tradeoffs.
Don't ask obvious questions, dig into hard parts.
Then write a spec to SPEC.md.
```

### Tip 29: Escape to Course-Correct
- `Esc` stops current action (context preserved)
- `Esc Esc` opens rewind menu
- "Undo that" asks Claude to revert

Course-correct early and often.

### Tip 30: Skills Over CLAUDE.md for Domain Knowledge
Skills load on-demand. CLAUDE.md loads every session.

Put frequently-needed rules in CLAUDE.md.
Put domain-specific knowledge in skills.
