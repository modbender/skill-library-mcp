---
name: context-recovery
description: Automatically recover working context after session compaction or when continuation is implied but context is missing. Works across Discord, Slack, Telegram, Signal, and other supported channels.
homepage: https://github.com/PSPDFKit-labs/agent-skills
repository: https://github.com/PSPDFKit-labs/agent-skills
metadata:
  {
    "openclaw":
      {
        "emoji": "🔄",
      },
  }
---

# Context Recovery

Automatically recover working context after session compaction or when continuation is implied but context is missing. Works across Discord, Slack, Telegram, Signal, and other supported channels.

**Use when**: Session starts with truncated context, user references prior work without specifying details, or compaction indicators appear.

---



## Safety Boundaries

- This skill prioritizes channel/session API history to recover context.
- It does NOT perform broad filesystem scans or shell glob searches by default.
- It does NOT send recovered context to external services.
- It does NOT write to disk unless the user explicitly asks to persist recovered state.
## Triggers

### Automatic Triggers
- Session begins with a `<summary>` tag (compaction detected)
- User message contains compaction indicators: "Summary unavailable", "context limits", "truncated"

### Manual Triggers
- User says "continue", "did this happen?", "where were we?", "what was I working on?"
- User references "the project", "the PR", "the branch", "the issue" without specifying which
- User implies prior work exists but context is unclear
- User asks "do you remember...?" or "we were working on..."

---

## Execution Protocol

### Step 1: Detect Active Channel

Extract from runtime context:
- `channel` — discord | slack | telegram | signal | etc.
- `channelId` — the specific channel/conversation ID
- `threadId` — for threaded conversations (Slack, Discord threads)

### Step 2: Fetch Channel History (Adaptive Depth)

**Initial fetch:**
```
message:read
  channel: <detected-channel>
  channelId: <detected-channel-id>
  limit: 50
```

**Adaptive expansion logic:**
1. Parse timestamps from returned messages
2. Calculate time span: `newest_timestamp - oldest_timestamp`
3. If time span < 2 hours AND message count == limit:
   - Fetch additional 50 messages (using `before` parameter if supported)
   - Repeat until time span ≥ 2 hours OR total messages ≥ 100
4. Hard cap: 100 messages maximum (token budget constraint)

**Thread-aware recovery (Slack/Discord):**
```
# If threadId is present, fetch thread messages first
message:read
  channel: <detected-channel>
  threadId: <thread-id>
  limit: 50

# Then fetch parent channel for broader context
message:read
  channel: <detected-channel>
  channelId: <parent-channel-id>
  limit: 30
```

**Parse for:**
- Recent user requests (what was asked)
- Recent assistant responses (what was done)
- URLs, file paths, branch names, PR numbers
- Incomplete actions (promises made but not fulfilled)
- Project identifiers and working directories

### Step 3: Fetch Session Context (safe mode)

Use platform/session APIs only (no shell filesystem scans):

```yaml
# List recent sessions (if tool exists)
sessions_list:
  limit: 5

# Pull last messages from likely matching session
sessions_history:
  sessionKey: <candidate-session-key>
  limit: 80
  includeTools: true
```

If session APIs are unavailable, skip this step and proceed with channel-only evidence.

### Step 4: Optional Memory Check (explicitly scoped)

Only inspect memory if the agent runtime already provides a scoped memory tool/path.
Do **not** run shell glob scans across home directories.

### Step 5: Synthesize Context

Compile a structured summary:

```markdown
## Recovered Context

**Channel:** #<channel-name> (<platform>)
**Time Range:** <oldest-message> to <newest-message>
**Messages Analyzed:** <count>

### Active Project/Task
- **Repository:** <repo-name>
- **Branch:** <branch-name>
- **PR:** #<number> — <title>

### Recent Work Timeline
1. [<timestamp>] <action/request>
2. [<timestamp>] <action/request>
3. [<timestamp>] <action/request>

### Pending/Incomplete Actions
- ⏳ "<quoted incomplete action>"
- ⏳ "<another incomplete item>"

### Last User Request
> "<quoted request that may not have been completed>"
```

### Step 6: Optional Persistence (consent-first)

Do not write to disk by default. If persistence is useful, ask first:

> "I can cache this recovered context to memory for later continuity. Should I save it?"

### Step 7: Respond with Context

Present the recovered context, then prompt:

> "Context recovered. Your last request was [X]. This action [completed/did not complete]. Shall I [continue/retry/clarify]?"

---

## Channel-Specific Notes

### Discord
- Use `channelId` from the incoming message metadata
- Guild channels have full history access
- Thread recovery: check for `threadId` in message metadata
- DMs may have limited history

### Slack
- Use `channel` parameter with Slack channel ID
- Thread context requires `threadId` — always check for thread context first
- Parent channel fetch provides surrounding conversation context
- May need workspace-level permissions for full history

### Telegram / Signal / Others
- Same `message:read` interface
- History depth may vary by platform
- Group vs. DM context may differ

---

## Constraints

- Prefer this protocol before declaring "insufficient data" when context appears missing
- Adaptive depth: start with 50, expand to 100 max
- Time-based goal: capture at least 2 hours of context when possible
- If recovery fails, state what was attempted and what data sources were unavailable
- Avoid broad filesystem scans or writes without explicit user consent

---

## Auto-Trigger Detection

At session start, scan for compaction indicators:

```python
# Pseudocode for trigger detection
if message contains "<summary>":
    trigger_context_recovery()
elif message contains any of ["Summary unavailable", "context limits", "truncated", "compacted"]:
    trigger_context_recovery()
elif message matches continuation_patterns:
    # "continue", "where were we", "did this happen", etc.
    trigger_context_recovery()
```

**Do not wait for user to ask** — if compaction is detected, proactively recover and present context.

---

## Example

**Scenario:** Session starts with compaction summary

```
User message: "<summary>Summary unavailable due to context limits...</summary>"
User message: "did this happen?"
```

**Agent executes:**
1. Detects compaction via `<summary>` tag
2. `message:read channel=discord channelId=1460342116516364533 limit=50`
3. Calculates time span: 2.5 hours — sufficient, no expansion needed
4. Parses messages, finds last action: "Now let me extract the key orchestration decisions..."
5. Checks session context APIs — extracts recent user requests
6. Responds:

> "Context recovered. Your last request was to extract orchestration decisions from Nexus archived sessions for PR #137 (Skills & Agents System). This action did not complete before context was truncated.
>
> **Recovered state:**
> - PR #137: 15,053 additions, 91 files, CONFLICTING merge state
> - Spec location: `content/spec-skills-agents-system.md` (2,067 lines)
>
> Shall I proceed with the extraction?"
