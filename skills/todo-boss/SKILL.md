# todo-boss

## Purpose
Task capture + delegation tracking + daily remaining-work report for Telegram.
NO web browsing, NO web search, NO external lookups.

## Data store
Append-only log: ~/.openclaw/workspace/data/todo/tasks.jsonl
Derived state cache (optional): ~/.openclaw/workspace/data/todo/state.json

## Commands (Telegram)
- /todo <text> : create a task draft from free text
- /todo_done <id> : mark done
- /todo_list : list open tasks (grouped by owner, then due date)
- /todo_delegated : list tasks I assigned to others that are still open (include history)
- /todo_report : daily report (same as list, but concise)

## Extraction rules (very important)
When user sends /todo <text>:
1) Extract: title, owner, due_date (YYYY-MM-DD or natural language), priority (optional), notes.
2) If owner OR due_date is missing/ambiguous:
   - Ask a follow-up question in Telegram.
   - Store as status="draft" with missing_fields=[...].
   - Do NOT finalize as "open" until both are confirmed.
3) If owner/due_date are present:
   - Create status="open"
4) Always echo back a confirmation summary: id, title, owner, due_date, status.

## Default assumptions
- If owner missing: ask "누가 담당할까요? (본인/팀원 이름)"
- If due_date missing: ask "납기는 언제로 할까요?"
- Timezone: Asia/Seoul.

## History
Any update must append an event to tasks.jsonl:
- created / finalized / updated / done / reopened
Include: timestamp, actor(user), previous values, new values.

## Hard constraints
- Never call web tools.
- Never require API keys.
- Keep replies short and action-oriented.

## Execution
When receiving /todo:
- Call: ~/.openclaw/workspace/skills/todo-boss/add_task.sh "<full user text after /todo>"
- Reply to user with the script output.

## Follow-up policy (strict)
Only ask these two questions if missing:
1) "담당자(owner)는 누구로 할까요?"
2) "납기(due)는 언제로 할까요?"

Do NOT ask about content details, background, meeting context, or email structure.
This skill is a task tracker, not a planning assistant.

If the user asks for planning or drafting, answer briefly but still capture the task by asking owner/due if missing.
