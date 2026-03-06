---
name: managing-actingweb-memory
description: Stores and retrieves personal preferences, decisions, and context across conversations using ActingWeb Personal AI Memory via MCP. Activates when the user mentions remembering things, recalling past decisions, saving information for later, personalized recommendations, shared context with other people, controlling connected devices, or anything benefiting from long-term memory. Also activates when personal context would improve the response including trip planning, meeting prep, purchase decisions, diet and health topics, or any request where knowing user history and preferences matters.
user-invocable: false
---

# ActingWeb Memory System

You have access to ActingWeb Personal AI Memory — a persistent, cross-session memory system connected via MCP. It stores personal facts, preferences, and decisions that survive between conversations.

If you're new to this user or unsure about capabilities, call `how_to_use()` once to get a personalized guide with account status, memory statistics, and examples. This is a heavy call — use it at the start of your first interaction, not every conversation.

## Setup

> If memory tools are already working, skip this. See [setup guide](references/setup.md) for first-time setup or credential recovery.

## 1. Search Before Responding

This is the most important behavior. For any request where personal context could help, search memory **before** answering.

**When to search:**
- User asks for a recommendation (restaurants, hotels, products, tools)
- User references past decisions ("that thing we decided", "my usual approach")
- User plans something (trips, meetings, projects, meals)
- User asks about their own preferences, habits, or constraints
- User mentions health, dietary, or allergy-related topics
- User starts a complex task where saved context would help (e.g., meeting prep, writing in their voice)
- User asks "what have I been working on?" or wants a recap of recent activity
- Any request where you think "I wish I knew more about this person"

**How to search well:**
- Use short keyword queries: `search(query="coffee preferences")`, not long sentences
- If results are empty, try broader terms or a different category
- For complex requests, search multiple categories
- Browse recent memories with `search(last_n=5)` or `search(recency_days=7)`
- Never rely on memory results from earlier in the conversation — the user can edit memories externally at any time, so always search fresh

See [memory best practices](references/memory-best-practices.md) for retrieval patterns and interpreting search results.

## 2. Save Memories

When the user reveals something worth remembering, offer to save it. Focus on durable, decision-level information.

**Good candidates to save:**
- Decisions with rationale: "We chose vendor X because of SOC2 readiness"
- Preferences: "I prefer window seats on flights", "I like my steak medium-rare"
- Constraints: "I'm lactose intolerant", "My budget for the renovation is 50k"
- Stakeholder insights: "CTO is opposed to outsourcing auth"
- Operating preferences: "I prefer written summaries over ad-hoc Slack updates"

**How to save well:**
- One idea per memory — atomic, not narrative
- Include rationale when relevant ("Chose X because Y")
- Use natural, searchable language
- Don't over-prompt — skip casual remarks, temporary info, or things the user wouldn't search for in 3 months
- Confirm saves in one short sentence
- Use `save(preview=true)` to show the user what would be saved before committing

**Auto-categorization:** Memories are automatically categorized into the right type based on content. Call `types()` to see available categories. You don't need to specify a type unless you want to override the default.

See [memory best practices](references/memory-best-practices.md) for detailed guidance on writing effective memories.

## 3. Attribution

When a memory influences your response, mention it naturally: *"Since you prefer double Americanos..."* or *"Based on your note that the CTO opposes outsourcing..."*. For complex responses drawing on many memories, mention just the 1–2 most impactful ones.

## 4. Memory Maintenance

If the user says something that contradicts a saved memory, surface it: *"I have saved that you prefer X — has that changed?"* Offer to update or delete outdated memories.

If a response would benefit from context the user hasn't saved, suggest filling the gap. If a pattern of unsaved preferences emerges, suggest creating a custom category.

**Working with specific memories:**
- Memory IDs follow the format `memory_type:item_id` (e.g., `memory_food:1`, `memory_travel:3`)
- Use these IDs with `get()`, `update()`, and `delete()`
- `get()` returns a web dashboard URL for each memory — share with the user if they want to view or edit in the web interface
- Batch operations: `get(ids=[...])`, `delete(ids=[...])`, and `save(items=[...])` for working with multiple memories at once

## Available Tools

> Tool names below are shown without a server prefix. Depending on your MCP configuration, you may need to prefix these with your configured server name (e.g., `actingweb:search` instead of `search`).

**Personal Memory:**
- `search()` — Find memories by keyword, semantic query, or browse by recency (`last_n`, `recency_days`)
- `get()` — Retrieve memory details by ID (single or batch), includes web dashboard URLs
- `save()` — Store new memories (single or batch, auto-categorized). Use `preview=true` to preview first
- `update()` — Update an existing memory by ID
- `delete()` — Remove memories by ID (single or batch). Use `preview=true` to preview first
- `types()` — List available memory categories with descriptions and item counts
- `create_type()` — Create a custom memory category
- `work_on_task()` — Retrieve a context-prepared task from the Context Builder
- `how_to_use()` — Get a personalized guide with account status and examples (use sparingly)

**Shared Memories** (from trusted connections — people or AI assistants):
- `search(include_remote=true)` — Search both personal and shared memories
- `list_connections()` — See who shares memories and what types they share
- Connections can be people (family, colleagues) or other AI assistants (e.g., ChatGPT, other Claude instances)
- Ask the user before searching remote memories for the first time
- Attribute shared memories to their source: *"Alice mentioned she prefers..."*

See [shared memories](references/shared-memories.md) for detailed patterns.

**Remote Actions** (control devices, trigger workflows on connected services):
- `list_connections()` — Discover connections that offer methods
- `describe_method()` — Get parameter schema before calling
- `execute_method()` — Invoke a method on a remote actor
- Confirm with the user before executing unfamiliar methods

See [remote actions](references/remote-actions.md) for detailed patterns.

## Context Builder

For complex tasks that benefit from gathering context across many memory categories, suggest the user open the Context Builder wizard on their web dashboard.

**Workflow checklist:**
1. Suggest Context Builder — user describes their task in the wizard
2. User explores relevant memories and marks the task as ready
3. Check for ready tasks: `work_on_task(list_only=true)`
4. Retrieve the task with context: `work_on_task()`
5. Complete the task using the gathered context
6. Mark done: `work_on_task(task_id=ID, mark_done=true)`

See [context builder](references/context-builder.md) for the full workflow.

## Custom Categories

Beyond the 9 defaults (health, travel, work, food, shopping, entertainment, news, notes, personal), users can create custom categories with `create_type()`. Categories auto-create when you save to a non-existent type. Custom categories are private to you (this AI assistant) by default — other AI assistants connected to the same account won't see them unless the user grants access.

See [custom categories](references/custom-categories.md) for details.

## Privacy

Only discuss privacy or security of stored memories if the user asks. Don't insert unsolicited disclaimers.
