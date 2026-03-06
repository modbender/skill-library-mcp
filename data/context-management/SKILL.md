---
name: context-management
version: 1.0.0
description: >
  Manage AI agent context window consumption, prevent compaction death spirals,
  and enforce sub-agent spawn policies. Use when: (1) context is filling up and
  work quality may degrade, (2) deciding whether to spawn a sub-agent or work in
  main session, (3) preparing for compaction or session handoff, (4) user asks
  "what's eating my context?" or "how much runway left?", (5) after compaction to
  restore working state from checkpoint files. NOT for: general memory/workspace
  management (use memory-keeper or workspace-standard).
---

# Context Management

Prevent context exhaustion, enforce spawn discipline, and make compaction survivable.

## Core Concepts

1. **Fixed baseline**: Typically 5-15% of context consumed before any conversation — system prompt, workspace files, skill descriptions, tool definitions. Varies by setup (more skills/files = higher baseline).
2. **60/40 rule**: ~60% of consumed context is tool outputs, ~40% conversation. Tool outputs are the primary target for savings.
3. **Compaction is lossy**: Summaries stack cumulatively. Each cycle raises the floor. After 3+ compactions, summaries alone can consume 30%+ of context.
4. **Sub-agents are disposable context**: A sub-agent can burn most of its context investigating something; only the summary (~500 tokens) enters main context.

All percentages are relative to the model's context window. Check `session_status` for actual window size and usage.

## Procedures

### When Context Pressure Rises

After every tool-heavy operation (>5 tool calls), assess:

1. Run `session_status` to check usage
2. If **below 50%**: continue normally
3. If **50-70%**: spawn sub-agents for remaining tool-heavy work (>3 tool calls)
4. If **70-85%**: spawn sub-agents for ANY tool work (>1 tool call). Warn user.
5. If **above 85%**: write checkpoint (see below), suggest `/compact` or `/new`

### "What's Eating My Context?" — Estimation Method

Cannot get exact per-component breakdown. Estimate:

```
Fixed baseline:         ~5-15% (system prompt + workspace files + skills + tools)
Per user message:       ~100-500 tokens each
Per assistant response: ~200-1000 tokens each
Per tool call result:   ~500-5000 tokens each (exec/read heavy, search light)
Compaction summaries:   ~2000-5000 tokens each (cumulative!)
```

Count messages and tool calls in recent history, multiply by midpoint estimates. Report as ranges, not false precision. For per-operation cost detail, read `references/operation-costs.md`.

### Spawn Policy

If `.context-policy.yml` exists in workspace root, use it as guidance for spawn thresholds and task categories. Otherwise use these defaults:

**Always spawn** (regardless of context level):
- Test suites (>3 tests)
- Multi-file audits (>5 files)
- Build/deploy pipelines
- Research tasks (web search + analysis)
- Bulk file operations

**Never spawn** (keep in main session):
- Single commands
- Conversations / discussions
- Quick edits (1-3 files)
- Status checks
- Tasks requiring user input mid-execution

**Context-dependent** (spawn when context exceeds threshold):
- Above 50%: spawn if task involves >5 tool calls
- Above 70%: spawn if task involves >2 tool calls

When spawning, write detailed task descriptions. Sub-agents have no conversation context — they only know what the task field tells them.

### Pre-Compaction Checkpoint

Before compaction or `/new`, write `.context-checkpoint.md` in the **workspace root** (the agent reads this post-compaction):

```markdown
# Context Checkpoint — {date} {time}

## Active Task
{what you were doing}

## Key State
{bullet list of current state — what's done, what's in progress}

## Decisions Made This Session
{numbered list of decisions with rationale}

## Files Changed
{list of files modified this session}

## Next Steps
{what to do after resuming}
```

This file survives compaction. On session start or post-compaction, check for it and use it to restore context. Delete after consuming.

**Coordination with OpenClaw memoryFlush:** OpenClaw may fire its own pre-compaction flush (writing to daily log). The checkpoint is complementary — the flush saves to the daily log, the checkpoint saves structured resume state. Both should exist. If the memoryFlush fires first, compaction may already be in progress. For critical sessions, write checkpoints proactively at 75%, don't wait for 85%.

The `scripts/context-checkpoint.sh` script handles basic write/read/clear. For the full 5-section checkpoint, write the file directly — multiline content works better that way.

### Post-Compaction Recovery

After compaction or `/new`:

1. Read `.context-checkpoint.md` if it exists
2. Read today's daily log if the workspace has one (e.g. `memory/{today}.md`)
3. Resume from the checkpoint's "Next Steps"
4. Delete the checkpoint file after restoring context

### Proactive Warning Template

When context exceeds 65%, warn:

```
⚠️ Context: {pct}% ({used}k/{total}k). Estimated runway: ~{remaining_calls}
tool calls. {recommendation}
```

Recommendations by level:
- 65%: "Spawning sub-agents for remaining tool-heavy work."
- 75%: "Recommend compacting soon. Writing checkpoint."
- 85%: "Context critical. Writing checkpoint now. Suggest `/compact` or `/new`."

## Session Profiling & Config Advice

After significant work (or on request), profile the current session and recommend config changes.

### Step 1: Classify the Session Pattern

Run `session_status`. Count approximate tool calls and message exchanges. Classify:

| Pattern | Signature | Example |
|---------|-----------|---------|
| **Tool-heavy** | Most context from tool results, many exec/read/web calls | Audits, migrations, test suites, debugging |
| **Conversational** | Most context from messages, few tool calls | Planning, discussion, decisions |
| **Mixed** | Roughly even split | Feature builds (discuss → code → test → discuss) |
| **Bursty** | Long quiet periods with intense tool bursts | Monitoring + incident response |

### Step 2: Recommend Config

There are four settings that matter. When explaining them to the user, always describe **what they do in practice**, not just the setting name:

**1. When to compress the conversation** (`reserveTokensFloor`)
How full the context gets before the agent summarises and compresses the history. A higher number means it compresses sooner — producing a shorter summary with more room left afterwards.
- `30000` — waits until nearly full. Risk: huge summary, little room after.
- `50000` — compresses at ~75% full. Good balance.
- `60000` — compresses early at ~70%. Maximum breathing room.

**2. How quickly old tool output is cleared** (`pruning TTL`)
After you stop talking for this long, the agent clears old command outputs, file reads, and search results from memory. Shorter = more aggressive cleanup.
- `5m` — only clears after 5 minutes of silence. Rarely fires during active work.
- `2m` — clears after 2 minutes. Good for most workflows.
- `1m` — aggressive. Clears fast, but you might need to re-read files.

**3. How many recent exchanges are protected from cleanup** (`keepLastAssistants`)
When clearing old tool output, this many of your most recent back-and-forth exchanges are kept untouched.
- `3` — keeps more history visible. Good for conversations.
- `2` — moderate protection.
- `1` — only the last exchange is safe. Most aggressive cleanup.

**4. Minimum size before tool output gets trimmed** (`minPrunableToolChars`)
Only tool results larger than this (in characters) are eligible for trimming. Lower = more things get cleaned up.
- `50000` (default) — only trims very large outputs (long file reads, huge command output).
- `10000` — also trims medium outputs. Catches more.
- `5000` — aggressive. Most tool results are eligible.

**Recommended combinations by work style:**

| Work style | Compress at | Clear after | Protect | Trim above | 
|------------|------------|-------------|---------|------------|
| Tool-heavy (audits, tests, debugging) | `60000` | `1m` | `1` | `10000` |
| Conversational (planning, discussion) | `30000` | `5m` | `3` | `50000` |
| Mixed (code → test → discuss) | `50000` | `2m` | `2` | `10000` |
| Bursty (monitoring + incidents) | `50000` | `2m` | `1` | `10000` |

Additional tips:
- **Sessions with browser/canvas work**: Ensure those tools are protected from cleanup in the config
- **Long-running sessions (>2h)**: Use a higher compression trigger to survive multiple rounds

### Step 3: Report

Use a compact list format — tables render poorly on mobile and narrow chat windows. For each setting, show current vs recommended only if they differ. Skip settings that are already correct.

```
📊 Current Session Profile: {pattern}
Context: {pct}% ({used}k/{total}k) · Compressions: {c}

✅ When to compress — {current_description}. Good for this work style.
✅ Clear old output after — {current_description}. No change needed.
⚠️ Protect last exchanges — currently {current}, recommend {recommended}. {why}
✅ Trim output above — {current_description}. No change needed.

Estimated runway: ~{time_or_calls} before next compression.
```

Lead with what's already right (builds confidence), then highlight what needs changing and why. Keep it short — the user wants a verdict, not a lecture.

If changes are recommended, tell the user **everything** up front before asking for approval:
1. **Exact file** being modified (full path — get from `gateway config.get`)
2. **Exact changes** — setting name, current value, new value
3. **What happens** — gateway restart (~2-3 second pause, auto-reconnects)
4. **Safety net** — backup taken first, rollback doc written to temp directory

Example closing:
```
One change recommended:
  File: {config_path}
  Change: {setting_name}: {old_value} → {new_value}
  
Applying means: I'll back up the config file first, write a rollback 
doc to {temp_path}, then restart the OpenClaw gateway (~2-3 second 
pause while it reloads). Want me to go ahead?
```

For multiple changes, list each one. Never summarise as "4 changes" — spell them out.

Never ask "want me to apply?" without the user seeing the exact file, exact values, and exact consequences. The user decides with full information, not blind trust.

If the user agrees, follow the full procedure below.

### Step 4: Learn Over Time

After giving advice, note the session pattern and outcome in the daily log (if the workspace keeps one). Over multiple sessions, patterns emerge — the user's typical work style becomes clear and default config can be permanently tuned.

## Applying Config Changes — Mandatory Procedure

When recommending config changes, follow this exact sequence. No shortcuts.

### 1. Find the Config File

Run `gateway config.get` to get the config file path and current values. Do not assume the path — it varies by installation.

### 2. Backup First
```bash
cp <config_path> <config_path>.backup-$(date +%Y%m%d-%H%M%S)
```

### 3. Write a Rollback Document

Write a rollback doc to a location the **user** can access (not the agent workspace — the user may not have access to it). Use a temp directory (`/tmp/` on Linux/macOS, or the system temp dir). Include:

```markdown
# Context Config Rollback — {date}

## What Changed
| Setting | Before | After | File |
|---------|--------|-------|------|
| {setting} | {old} | {new} | {config_path} |

## Backup Location
{config_path}.backup-{timestamp}

## How to Rollback
cp {backup_path} {config_path}

## How to Restart the Gateway
Depends on local setup — check which applies:
- CLI (most common): openclaw gateway restart
- systemd service: sudo systemctl restart <service-name>
- Manual process: kill the gateway process, then: openclaw gateway start

## How to Check Health
- Process running: check for openclaw in process list
- Gateway responding: curl http://localhost:<port>/health
- Logs: check system logs or terminal output depending on setup

## What to Do If Gateway Won't Start
1. Restore backup (cp command above)
2. Restart gateway
3. Check logs for config parse errors
```

Tell the user where this file is.

### 4. Explain to the User BEFORE Applying
Tell them:
- **Which file** is being modified (full path — get it from `gateway config.get`)
- **What values** change (before → after table)
- **What "restart" means** — the OpenClaw gateway process restarts (not the machine, not any other service). Brief 2-3 second pause, then the session reconnects automatically.
- **Where the backup is** (full path)
- **Where the rollback doc is** (full path)
- **How to check** if something goes wrong

### 5. Apply with gateway config.patch
Use the `gateway` tool with `action: config.patch`. Include a clear `note` parameter — this message is delivered to the user after the gateway restarts.

### 6. Post-Restart Confirmation (MANDATORY)
After the gateway restarts and the session reconnects, **immediately confirm to the user**:

```
✅ Gateway is back. Config changes applied successfully.

What changed:
- {setting}: {old} → {new} ({plain English explanation})
- [etc.]

Rollback doc: {path}
Backup: {path}

Everything is working normally. Ready to continue.
```

**Never stay silent after a restart.** The user needs to know:
1. We're back
2. The changes landed
3. Where to find the rollback doc
4. That we're ready to continue

## Reference Docs

For detailed config options and profiles: `references/config-guide.md`
For per-operation cost estimates: `references/operation-costs.md`
