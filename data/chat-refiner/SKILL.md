---
name: chat-refiner
description: Refine conversation history by deleting useless/redundant/process exchanges. Keep explicit instructions, disciplines, important configs, skills learned (how), user &#39;remember this&#39; info. Use when user asks to summarize/clean chat logs, sessions_history, or memory maintenance. Produces concise MEMORY.md updates or summary files.
---

# Chat Refiner

## When to Use

User requests:
- &quot;精简聊天记录&quot;
- &quot;clean/summarize history&quot;
- &quot;update MEMORY.md from transcripts&quot;
- Memory maintenance during heartbeats.

## Workflow

1. **Input**: sessions_history (this session or other), memory/*.md, chat transcripts.
2. **Principles** (see references/principles.md):
   - Delete casual/heartbeats/repeated tools.
   - Keep: disciplines, configs, skills learned/install, explicit &quot;remember&quot;, decisions.
3. **Process**:
   - Read raw.
   - Extract key.
   - Write summary to memory/YYYY-MM-DD-summary.md or MEMORY.md.
4. **Output**: Clean file + &quot;Refined X items kept&quot;.

## Tools

- sessions_history: fetch transcripts.
- memory_search/get: prior context.
- write/edit: output summary.

## Examples

User: &quot;精简对话&quot; → read history → refine → write memory/summary.md.

Ref: [principles.md](references/principles.md)