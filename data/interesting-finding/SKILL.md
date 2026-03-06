---
name: interesting-finding
description: Process links and content shared in the #interesting-finding Discord channel. Use when: (1) a URL or article is shared in #interesting-finding, (2) someone asks to log or analyze content from #interesting-finding, (3) performing a heartbeat check and #interesting-finding has new unread content. Workflow: fetch URL → analyze → create Discord thread → post summary to thread → save distilled notes to knowledge base (memory/kb/).
---

# interesting-finding Workflow

## Channel Details

- **Channel:** `#interesting-finding`
- **Channel ID:** `1471924730113163398`
- **Rule:** Every response MUST be in a thread — never reply in the main channel.

## Step-by-Step Workflow

### 1. Fetch the content

```
web_fetch(url)
```

Extract the main body. If the URL fails, try `web_search` with the title as fallback.

### 2. Analyze and summarize

Produce a compact analysis (not a full recap). Include:
- **核心观点** — what's the key argument or finding?
- **为什么有意思** — relevance to Sober's interests (AI, dev tools, self-hosting, health, psychology)
- **可行动的部分** — anything concrete to try, apply, or follow up on
- **相关链接/来源** (if any)

Keep it under 500 chars for Discord thread readability. Dense > verbose.

### 3. Create Discord thread (CRITICAL: follow exactly)

```
# Step A — create thread (NO message param)
message(action=thread-create, messageId=<original_message_id>, threadName=<short title>)

# Step B — send analysis to the thread
message(action=send, target=<threadId returned from step A>, message=<analysis>)
```

⚠️ **Common mistakes:**
- ❌ Do NOT pass `message` param to `thread-create` — it won't appear in the thread
- ❌ Do NOT use `thread-reply` — it posts to the main channel instead
- ✅ `threadId` = same as original `messageId`

### 4. Save to knowledge base

Append a distilled note to the appropriate `memory/kb/` file:

| Topic | File |
|-------|------|
| AI / agents / coding tools | `memory/kb/build.md` |
| Self-hosting / DevOps / infra | `memory/kb/ops.md` |
| Health / psychology / life | `memory/kb/grow.md` |
| Economics / future of work | `memory/kb/think.md` |
| Misc / doesn't fit above | `memory/kb/misc.md` |

**KB entry format:**
```markdown
### [YYYY-MM-DD] Title or short description
- Source: <url>
- Key insight: <1-2 sentences>
- Why it matters: <optional, if non-obvious>
- Action: <optional, concrete next step>
```

### 5. Git commit

```bash
cd /home/sober/clawd && git add memory/kb/ && git commit -m "kb: add [topic] note from #interesting-finding"
```

## Heartbeat Check

During heartbeat, scan #interesting-finding for new messages:

```
message(action=read, channel=1471924730113163398, limit=10)
```

Process any unprocessed links (no existing thread). Skip messages that already have threads or are just casual comments.

## Tone for Thread Posts

- 中文优先（Sober 是中文用户）
- 直接进入正题，不写"这篇文章讲了…"这种废话
- 有主见 — 说值不值得读，为什么有意思
- 对不值得深挖的东西也可以直接说"不重要"
