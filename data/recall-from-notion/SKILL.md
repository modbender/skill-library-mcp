---
name: recall-from-notion
description: >
  Recall user memories from the Notion Memory Store. Trigger PROACTIVELY at the beginning of
  conversations where knowing the user's background, preferences, past decisions, or project
  context would improve the response. Also trigger when the user says "回忆一下", "recall",
  "你还记得吗", "之前我们讨论过", "based on what you know about me", or references past context.
user-invocable: true
---

# Recall from Notion

Read the user's memories from the **Memory Store** Notion Database and use them as context
for the current conversation.

## Database Discovery

This skill uses a **zero-config convention**: the database is always named **"Memory Store"**.
No configuration files or environment variables are needed.

**Discovery flow (execute at Step 1):**

1. Search Notion for the database: `Notion:notion-search` with `query: "Memory Store"`
2. From the results, find an item that is a **database** (not a page) named "Memory Store".
   Extract its `data_source_id` from the result.
3. **If found** -> use this `data_source_id` for all subsequent operations.
4. **If not found** -> no memories exist yet. Silently skip recall and proceed with the
   conversation without injecting any memory context. Do NOT prompt the user to create anything.

## When to Trigger

**Always trigger when:**
- User references past conversations or shared context ("我们之前说的", "you know my setup")
- User starts a task where personal context matters (coding, writing, planning, recommendations)
- User asks about their own preferences, decisions, or project details
- User says "recall", "回忆", "你记得吗", or similar

**Consider triggering when:**
- A new conversation starts with a domain-specific task (coding, architecture, DevOps, etc.)
- User mentions a project name, tool, or technology that might have stored context
- User asks for recommendations or opinions where past preferences would help

**Skip when:**
- Pure factual Q&A with no personal dimension ("Python 的 GIL 是什么")
- User explicitly says they want a fresh start or generic advice

## Recall Strategy: Topic-Driven Smart Recall

The goal is **relevance over coverage**. Analyze the conversation topic first, then make
targeted searches. Different strategies apply depending on the estimated memory count.

### Step 1: Discover Database

Search Notion for "Memory Store" database. If not found, silently skip all remaining steps.

### Step 2: Analyze Conversation Topic

From the user's first message (or the current conversation context), extract:

1. **Primary keywords**: Specific nouns, technologies, tools, project names directly mentioned
   - e.g., "Notion", "Claude Code", "记忆层", "Python"
2. **Domain**: The broad topic area
   - e.g., coding, architecture, workflow, DevOps, personal, writing
3. **Intent**: What the user is trying to do
   - e.g., build, debug, decide, learn, configure, discuss
4. **Current project** (if in Claude Code): Detect from the working directory or conversation context
   - e.g., "OpenClaw", "skills", "claude_world"

### Step 3: Tiered Search Strategy

Run **2 searches** (not 3-5), designed to balance precision with coverage:

**Search 1 -- Topic Search (precision)**:
Use the primary keywords extracted in Step 2. This is the most important search.
```
query: "<primary keywords from user's message>"
data_source_url: "collection://<data_source_id>"
```

**Search 2 -- Broad Preference & Fact Sweep (coverage)**:
Always search for the user's core preferences and facts. These are useful in almost
any conversation, even if not directly related to the current topic.
```
query: "用户偏好 工具 习惯 决策"
data_source_url: "collection://<data_source_id>"
```

**Search 3 -- (Optional) Domain Expansion**:
Only if Search 1 returns fewer than 3 results AND the topic is clearly specific:
```
query: "<domain + broader related terms>"
data_source_url: "collection://<data_source_id>"
```

> **Why 2 searches instead of 5?**
> With <50 memories, Notion's semantic search is good enough that 2 well-crafted queries
> cover most relevant results. With 50-100+ memories, precision matters more than
> breadth -- noise from wide searches degrades context quality. Adding a 3rd search
> is reserved for when the first two don't return enough.

### Step 4: Filter

After collecting results, apply these filters:

**Scope filter (most important for Claude Code):**
- Always include: Scope = Global memories (universal preferences, facts)
- Include: Scope = Project memories where Project matches the current project name
- Exclude: Scope = Project memories for OTHER projects (these are noise)
- Include: memories with no Scope set (legacy data, treat as Global)

**Status filter:**
- **Status = Contradicted**: Superseded memories, always skip
- **Status = Archived**: Skip unless user explicitly asks for old memories

**Expiry filter:**
- 30d: Source Date + 30 days < today -> skip
- 90d: Source Date + 90 days < today -> skip
- 1y: Source Date + 1 year < today -> skip
- Never: Always include

For speed: if total results are <10, skip individual page fetches and include
everything (Contradicted memories are rare). Only do detailed filtering when
results exceed 10.

### Step 5: Deduplicate and Rank

Merge results from all searches.

**Priority scoring:**
1. **Multi-hit bonus**: Same memory found in both searches -> highest relevance
2. **Topic match**: Directly relates to user's current question/task
3. **Category weight**: Preference > Fact > Decision > Pattern > Skill > Context
4. **Confidence**: High > Medium > Low
5. **Recency**: Newer Source Date > Older

**Injection limit: 10-15 memories maximum.**

If more than 15 qualify:
- Always include: all Preference and Decision memories that scored high
- Include: top-ranked Fact and Skill memories
- Defer: Context and Pattern memories with lower relevance scores
- Briefly note that more memories exist if the user wants them

### Step 6: Inject as Context

Format recalled memories as a compact context block. Don't dump raw database rows --
synthesize into a readable briefing grouped by Category.

**Format:**

```
Recalled context from Memory Store:

[Preferences]
- 用户偏好用 Ruff 做代码格式化和 lint
- ...

[Facts]
- Notion 工作区已连通，集成方式为 MCP
- ...

[Decisions]
- Memory Store 采用 Notion Database 结构
- ...

[Skills]
- Claude Code /simplify: 自动代码审查，三个并行代理
- ...
```

Rules:
- Group by Category
- Keep each entry to 1-2 lines
- Include key details (IDs, commands, URLs) verbatim
- Only include Categories that have recalled entries (don't show empty groups)
- If a memory is clearly irrelevant to the current conversation despite being
  returned by search, silently drop it -- don't inject noise

### Step 7: Update "Last Used" (Low Priority)

After the conversation, update `Last Used` on memories that actually influenced
the response. Use `Notion:notion-update-page`:

```json
{
  "command": "update_properties",
  "page_id": "<memory_page_id>",
  "properties": {
    "date:Last Used:start": "YYYY-MM-DD",
    "date:Last Used:is_datetime": 0
  }
}
```

This is **low priority** -- do it at the end of the conversation or skip if it would
slow down the interaction. Its purpose is to enable future "least recently used" cleanup.

## Handling Edge Cases

**No results:**
- Don't force it. Just proceed without memories.
- Don't announce "Memory Store 中没有找到相关记忆" unless user explicitly asked for recall.

**Too many results (>15):**
- Apply the ranking strictly, inject top 10-15 only.
- Mention "Memory Store 中还有更多记忆可供参考" at the end of context block.

**Stale or wrong memories:**
- If a recalled memory contradicts the current conversation, flag it:
  "我注意到 Memory Store 里记录了 X，但你现在说的是 Y，要我更新吗？"
- This turns recall into a self-healing loop.

**User asks "你怎么知道的？":**
- Explain it came from Memory Store and offer to show or edit the entry.

## Important Notes

- **Speed over perfection**: 2 fast searches, merge, go. Don't over-optimize.
- **Silent injection**: Don't say "我正在搜索记忆库..." unless user explicitly asked.
  Just inject context and use it naturally in responses.
- **Relevance filter is key**: The biggest improvement over the old approach is
  NOT injecting irrelevant memories. When in doubt about relevance, leave it out --
  the user can always ask "你还记得 X 吗？" to trigger targeted recall.
- **Scope awareness**: In Claude Code, always detect the current project and filter
  memories accordingly. Global memories are always relevant; Project memories are only
  relevant when working in that specific project.
- **Cross-platform memories**: The Memory Store may contain entries from Claude.ai,
  Claude Code, OpenClaw, etc. Treat all sources equally.
- **Read-only**: This skill only reads. Writing/updating is handled by memory-to-notion.
  The only write is the optional "Last Used" timestamp.
